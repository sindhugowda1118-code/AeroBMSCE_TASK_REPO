import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from server.app import create_server


class RegistrationApiTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "members.sqlite3"
        self.server = create_server("127.0.0.1", 0, self.database_path)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary_directory.cleanup()

    def request(self, payload, content_type="application/json"):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        request = Request(
            f"{self.base_url}/api/interest",
            data=body,
            headers={"Content-Type": content_type},
            method="POST",
        )
        try:
            response = urlopen(request, timeout=3)
        except HTTPError as error:
            with error:
                return error.code, json.loads(error.read())
        with response:
            return response.status, json.loads(response.read())

    @staticmethod
    def valid_payload(**overrides):
        payload = {
            "fullName": "Aero Member",
            "email": "member@example.edu",
            "department": "Mechanical Engineering",
            "studyYear": "2",
            "interest": "aircraft-design",
            "consent": True,
        }
        payload.update(overrides)
        return payload

    def test_registration_is_persisted_and_duplicate_is_rejected(self):
        status, response = self.request(self.valid_payload())
        self.assertEqual(status, 201)
        self.assertEqual(response["message"], "Your interest has been saved.")

        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.server = create_server("127.0.0.1", 0, self.database_path)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"
        status, response = self.request(self.valid_payload(email="MEMBER@example.edu"))
        self.assertEqual(status, 409)
        self.assertIn("already", response["error"])

    def test_invalid_fields_are_reported_without_writing(self):
        status, response = self.request(
            self.valid_payload(email="not-an-email", studyYear="9", consent=False)
        )
        self.assertEqual(status, 400)
        self.assertEqual(set(response["fields"]), {"email", "studyYear", "consent"})

    def test_database_failure_returns_service_error(self):
        self.server.database_path = Path(self.temporary_directory.name) / "missing" / "db.sqlite3"
        with self.assertLogs("server.app", level="ERROR"):
            status, response = self.request(self.valid_payload())
        self.assertEqual(status, 503)
        self.assertIn("try again", response["error"])

    def test_health_endpoint_and_non_json_rejection(self):
        with urlopen(f"{self.base_url}/api/health", timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.loads(response.read())["status"], "ok")
        status, response = self.request(b"{}", "text/plain")
        self.assertEqual(status, 415)
        self.assertIn("JSON", response["error"])


if __name__ == "__main__":
    unittest.main()
