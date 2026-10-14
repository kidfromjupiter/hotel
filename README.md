# SkyNest Hotels

SkyNest is a hotel booking and guest services system for guests, receptionists, and administrators. Guests can browse rooms and manage reservations, receptionists can handle stays and charges, and administrators can review hotel operations and reports.

## What the project does

- **Guests:** Search room availability, complete a booking with OTP verification, sign in, and view their account and reservations.
- **Receptionists:** Look up bookings, check guests in, extend stays, add services, view invoices and payment status, record payments, and check guests out.
- **Administrators:** View occupancy and revenue reports, export reporting summaries, review branches and reservations, and create rooms.
- **Database:** PostgreSQL stores hotel data and enforces booking and billing rules through migrations, functions, and triggers.

## Technology and structure

| Directory | Purpose |
| --- | --- |
| `frontend/` | Next.js, React, and TypeScript interface |
| `backend/` | FastAPI application, API routes, services, repositories, and pytest suites |
| `db/` | PostgreSQL initialization, Flyway migrations, and seed data |
| `.github/workflows/` | GitHub Actions test workflow |

Docker Compose runs the frontend, backend, PostgreSQL, migrations, and seed process together. The API is served under `/api/v1`, with interactive documentation at `/docs`.

## Run locally

Install Docker with the Compose plugin, then run this from the repository root:

```sh
docker compose up --build
```

| Service | Local address |
| --- | --- |
| Web app | <http://localhost:3000> |
| API and documentation | <http://localhost:8000> and <http://localhost:8000/docs> |
| PostgreSQL | `localhost:5431` |

The default frontend API URL is `http://localhost:8000`. To stop the stack, run `docker compose down`. Add `--volumes` only when you want to reset the local database.

## Run tests

The backend has unit, API, and PostgreSQL tests. The test Compose stack starts a separate database, applies migrations, loads seed data, and runs all three suites:

```sh
docker compose -f docker-compose.tests.yml run --build --rm tests
docker compose -f docker-compose.tests.yml down --volumes
```

GitHub Actions runs the same test command for pull requests and pushes to `main`.

## Team contributions

### Shavini Kaveesha

- **Frontend:** Integrated service charging, invoice viewing, and checkout into the receptionist portal.
- **Backend:** Developed services, billing, and checkout APIs; implemented JWT staff login and role-based access.
- **Database:** Created booking, billing, and checkout functions; automated membership discounts, invoice updates, and room availability.

### Thisangi Dewmini

- **Frontend:** Built the administrator and receptionist interfaces, guest login, and My Account UI.
- **Backend:** Implemented guest authentication and administrator reservation retrieval.
- **Database:** Designed tables, relationships, and seed data; added the double-booking prevention trigger.

### Aloka Fernando

- **Frontend:** Built guest and receptionist UI.
- **Backend:** Implemented the OTP workflow and adding services to bookings.
- **Database:** Added the `otp_log` table and indexes.

### Lasan Mahaliyana 

- **Frontend:** Connected room availability, extended stays, service charges, and payment status to the receptionist and booking flows.
- **Backend:** Developed and refactored booking and room APIs, added extended-stay and payment flows, and established a clear database access boundary.
- **Database and tooling:** Set up Docker Compose, migrations and seed data, database tests, and the GitHub Actions test pipeline.

### Visvalingam Banujan

- **Frontend:** Built admin room creation; fixed reporting and added CSV export; improved dashboard charts and error handling.
- **Backend:** Developed admin room creation APIs, refactored the service-charge repository, and added report validation and branch access controls.
- **Database:** Implemented primary-key generation with PostgreSQL identities and seed sequence synchronization; wrote database concurrency and persistence tests.
