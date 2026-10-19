#!/usr/bin/env python3
"""Small, dependency-free web server and SQLite API for AeroBMSCE."""

from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = ROOT / "data" / "aerobmsce.sqlite3"
MAX_BODY_BYTES = 8_192
INTERESTS = {
    "aircraft-design",
    "uav-systems",
    "autonomy",
    "fabrication",
    "research",
    "partnership",
}
YEARS = {"1", "2", "3", "4", "graduate", "other"}
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class DuplicateSubmission(Exception):
    """Raised when an email address has already registered interest."""


class InvalidSubmission(Exception):
    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        super().__init__("The registration contains invalid fields.")


def connect_database(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


@contextmanager
def database_connection(database_path: Path):
    connection = connect_database(database_path)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with database_connection(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS member_interest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                department TEXT NOT NULL,
                study_year TEXT NOT NULL,
                interest TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
    if os.name != "nt":
        database_path.chmod(0o600)


def validate_submission(payload: object) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not isinstance(payload, dict):
        raise InvalidSubmission({"form": "Send the form as a JSON object."})

    allowed = {"fullName", "email", "department", "studyYear", "interest", "consent"}
    if set(payload) - allowed:
        raise InvalidSubmission({"form": "The form contains an unsupported field."})

    fields = ("fullName", "email", "department", "studyYear", "interest")
    if any(not isinstance(payload.get(field), str) for field in fields):
        raise InvalidSubmission({"form": "Complete each required field and try again."})

    full_name = payload["fullName"].strip()
    email = payload["email"].strip().lower()
    department = payload["department"].strip()
    study_year = payload["studyYear"].strip()
    interest = payload["interest"].strip()

    if not full_name or len(full_name) > 100 or any(ord(char) < 32 for char in full_name):
        errors["fullName"] = "Enter your name (up to 100 characters)."
    if len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        errors["email"] = "Enter a valid email address."
    if not department or len(department) > 100:
        errors["department"] = "Enter your department (up to 100 characters)."
    if study_year not in YEARS:
        errors["studyYear"] = "Choose your current year of study."
    if interest not in INTERESTS:
        errors["interest"] = "Choose an area you would like to explore."
    if payload.get("consent") is not True:
        errors["consent"] = "Please agree to be contacted about this enquiry."
    if errors:
        raise InvalidSubmission(errors)

    return {
        "full_name": full_name,
        "email": email,
        "department": department,
        "study_year": study_year,
        "interest": interest,
    }


def save_submission(database_path: Path, payload: object) -> int:
    submission = validate_submission(payload)
    try:
        with database_connection(database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO member_interest
                    (full_name, email, department, study_year, interest, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    submission["full_name"],
                    submission["email"],
                    submission["department"],
                    submission["study_year"],
                    submission["interest"],
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                ),
            )
            return int(cursor.lastrowid)
    except sqlite3.IntegrityError as error:
        if "member_interest.email" in str(error).lower():
            raise DuplicateSubmission from error
        raise


class ApplicationServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], database_path: Path):
        self.database_path = database_path
        super().__init__(address, ApplicationHandler)


class ApplicationHandler(SimpleHTTPRequestHandler):
    server_version = "AeroBMSCE/1.0"
    sys_version = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
        )
        super().end_headers()

    def list_directory(self, path: str):
        self.send_error(404, "Directory listing is disabled.")
        return None

    def _json_response(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        route = urlsplit(self.path).path
        if route == "/api/health":
            try:
                with database_connection(self.server.database_path) as connection:
                    connection.execute("SELECT 1")
            except sqlite3.Error:
                logging.getLogger(__name__).exception("Database health check failed.")
                self._json_response(503, {"error": "The database is unavailable."})
                return
            self._json_response(200, {"status": "ok"})
            return
        if route.startswith("/api/"):
            self._json_response(404, {"error": "API route not found."})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/interest":
            self._json_response(404, {"error": "API route not found."})
            return
        if self.headers.get_content_type() != "application/json":
            self._json_response(415, {"error": "Send this form as JSON."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json_response(400, {"error": "The request size is invalid."})
            return
        if length <= 0 or length > MAX_BODY_BYTES:
            self._json_response(413, {"error": "The form is empty or too large."})
            return
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json_response(400, {"error": "The request is not valid JSON."})
            return
        try:
            record_id = save_submission(self.server.database_path, payload)
        except InvalidSubmission as error:
            self._json_response(400, {"error": "Check the highlighted fields.", "fields": error.errors})
            return
        except DuplicateSubmission:
            self._json_response(
                409,
                {"error": "We could not add this request. Contact the team if you already submitted one."},
            )
            return
        except sqlite3.Error:
            logging.getLogger(__name__).exception("SQLite could not save a member interest request.")
            self._json_response(503, {"error": "We could not save your request right now. Please try again later."})
            return
        self._json_response(201, {"message": "Your interest has been saved.", "id": record_id})

    def log_message(self, format: str, *args) -> None:
        if os.environ.get("AEROBMSCE_ACCESS_LOG", "0") == "1":
            super().log_message(format, *args)


def create_server(host: str = "127.0.0.1", port: int = 8000, database_path: Path | None = None):
    resolved_path = database_path or Path(
        os.environ.get("AEROBMSCE_DB_PATH", str(DEFAULT_DB_PATH))
    )
    initialize_database(resolved_path)
    return ApplicationServer((host, port), resolved_path)


def main() -> None:
    if os.name != "nt":
        os.umask(0o077)
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    server = create_server(host, port)
    print(f"AeroBMSCE site and API listening on http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping AeroBMSCE server.", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
