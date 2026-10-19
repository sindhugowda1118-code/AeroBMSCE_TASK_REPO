# AeroBMSCE project website

A responsive, multi-page student project website for AeroBMSCE, the aerospace, aeromodelling and unmanned systems club at BMS College of Engineering. This is not the official club website.

## Run locally

The website and its registration API use Python's standard library and SQLite; no Python packages are required. From the repository root:

```powershell
$env:HOST = "127.0.0.1"
$env:PORT = "8000"
$env:AEROBMSCE_DB_PATH = "$PWD\data\aerobmsce.sqlite3"
python server\app.py
```

Open `http://127.0.0.1:8000/`. The SQLite file is created on first run. Stop the server with `Ctrl+C`. To run the API integration tests in a separate terminal:

```powershell
python -m unittest discover -s tests -v
```

The tests cover successful registration, persistence across a server restart, case-insensitive duplicate rejection, field validation, non-JSON requests, database outages and the health endpoint.

## Registration API and data

The Join page submits same-origin JSON to `POST /api/interest`. The required JSON fields are `fullName`, `email`, `department`, `studyYear`, `interest` and `consent`. `studyYear` accepts `1`, `2`, `3`, `4`, `graduate` or `other`; `interest` accepts `aircraft-design`, `uav-systems`, `autonomy`, `fabrication`, `research` or `partnership`; `consent` must be `true`.

- `201`: the interest request was written to SQLite.
- `400`: invalid form data, with field errors where possible.
- `409`: an interest request already exists for that email address.
- `413` / `415`: the request body is too large or is not JSON.
- `503`: the database could not save the request.

`GET /api/health` checks that the database can be queried. The database stores a name, email, department, year of study, selected interest and UTC submission time. It does not store passwords and does not create authenticated user accounts: this is a user-interest registration flow, not a login system. Entries are not publicly listed and there is no public admin interface. Collect only real enquiries, restrict database/backup access to trusted operators, set a retention period, and honor removal requests.

The server limits request bodies to 8 KiB, validates fields on the server, uses parameterized SQL, enforces a case-insensitive unique email, avoids logging request contents by default, disables directory listings and sets baseline browser security headers. On POSIX hosts the SQLite file is restricted to its owner and the app uses a restrictive umask. Use HTTPS and configure request-rate limiting at the production reverse proxy for a public form.

## Docker deployment

With Docker Engine and the Compose plugin installed:

```powershell
docker compose up --build -d
```

The app listens on port `8000`; its SQLite database persists in the named `aerobmsce-data` volume. Check readiness with `http://localhost:8000/api/health`, and stop it with `docker compose down` (the named data volume is retained). To remove stored registrations as well, an operator must deliberately remove that named volume; do not do so before taking any required backup.

For production, deploy the container on a host that supports persistent disk volumes, route HTTPS traffic to port 8000 through a TLS-terminating proxy, configure proxy-level rate limiting, and establish encrypted backups and a data-retention/deletion process. SQLite is intended for one app instance on a persistent local volume; use a managed database and an application change before scaling across multiple instances. No API keys or other secrets are needed by this implementation. No production host, persistent volume, or domain has been provisioned for this repository.

## GitHub Pages and the current live site

GitHub Pages can serve the static HTML, CSS, JavaScript and images, but it cannot run this Python API or SQLite database. On a Pages-only copy the registration request will fail visibly and visitors can use the supplied email contact instead. The database-backed experience works only when the site is served by `server/app.py` on a Python/Docker host; it is not safe to claim the Pages site has a working database.

The fork's existing Pages configuration points to `sindhugowda1118-code-aerobmsce-site-redesign` at `/(root)`. This implementation is on a separate feature branch and does not change that source or disturb the currently published URL:

- Existing live URL: <https://sindhugowda1118-code.github.io/AeroBMSCE_TASK_REPO/>
- Repository: <https://github.com/sindhugowda1118-code/AeroBMSCE_TASK_REPO>

Moving to a live database-backed version requires an operator to provision and configure the external Python/Docker host, persistent storage, HTTPS and backups. Those hosting resources are not available from this repository, so deployment of the API/database is not included.

## Content and source notes

- The supplied source describes the club as established in 2012 and representing more than 10 departments. Confirm those details before official publication.
- Competition entries, including current-season results, are transcribed from supplied source material and are not independently verified. Conflicting aggregate totals are omitted.
- Research directions, contact details and the Propel Lab–3 location may be stale and should be confirmed with the team.
- Partner categories and example benefits are proposals from the source, not confirmed sponsorship terms or relationships.
- The site uses the supplied AeroBMSCE mark and a locally bundled BMSCE college logo sourced from the official college website at `https://bmsce.ac.in/assets/img/bmsce_logo.jpg`. The marks are labelled separately; this project website is not the official club website.

## Recruitment task notes

### 1. What were the most noticeable flaws in the original website?

The starter pages used a fixed content width, inconsistent navigation, low-contrast text, non-responsive image sizing and removed keyboard focus indicators. Some page destinations were missing or misleading. This version provides a consistent responsive navigation system, real page destinations and accessible focus states. It also keeps verification caveats beside source-listed claims.

### 2. What was the design route, and what UI/UX decisions were made?

The visual direction adapts the supplied BMSCE PULSE reference into an aerospace context: warm ivory surfaces, ink-dark navigation, electric-blue calls to action, coral details, a lime flight accent, cinematic supplied photography and oversized editorial headings. A manually controlled, accessible homepage hero highlights aircraft, unmanned systems and the student team; shared navigation and page-specific heroes keep the same visual language throughout the site. The information architecture gives the club, projects, journey, partners and contact distinct pages. The join experience uses a server-validated form and a persistent SQLite record rather than a browser-only success state. Relative page and asset paths keep the static pages compatible with a repository subpath.

### 3. Describe one problem or edge case encountered, how it appeared, and the steps taken to work around it.

GitHub Pages cannot execute the Python API or persist SQLite records, so a Pages-only form would fail. The site now has a self-contained Python server/API and Docker setup for a host with persistent storage; the existing Pages source is left unchanged until that external deployment is provisioned and tested. The join page is expected to show a clear error and the email fallback if the API is not available.

## Original deployment instructions

Do not change the existing Pages source branch as part of this feature work. A static version can still be viewed on the existing live URL above. The separate Docker-backed website should be switched into public use only after the external host, persistent volume, HTTPS, backups, frontend, API and database have all been tested together.
