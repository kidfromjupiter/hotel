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

## Hotel and billing rules

- `CONFIRMED` is the stored status for a booked room. Check-in and paid checkout change it to `CHECKED_IN` and `CHECKED_OUT` and update the room's occupied/available state in the same transaction.
- The database prevents overlapping active bookings, including concurrent requests. Availability records for a date range come from `room_availability(start_date, end_date)`; the end date is exclusive.
- A room's booked rate and membership discount are captured when the booking is made. Service usage stores its date, quantity, unit price, and discount at the time of use. Only checked-in bookings can receive service charges or payments.
- This academic demo uses the seeded membership discounts and one active, configurable 15% tax on discounted room and service charges. It is a project assumption, not a statement of Sri Lankan tax law. There is no late checkout charge.
- A bill must be fully paid before checkout. Monthly branch revenue uses the month payments were received and shows room, service, and tax amounts separately. Partial payments remain visible as outstanding balances.
- Fresh installations seed 3 branches, 15 rooms, 7 services, 5 guests, 8 bookings, and 3 partially paid checked-in stays. The test stack uses an isolated temporary database.

The reporting model uses room nights and occupancy rate, which are also reported in the [Sri Lanka Tourism Development Authority's accommodation statistics](https://sltda.gov.lk/storage/documents/d0b10601f0cedd91115f9774a935c6d8.pdf). Room types and capacities are modeled separately in line with the authority's [hotel classification materials](https://www.sltda.gov.lk/en/register-with-us). Tax, discounts, and checkout charges above are explicit demo policies.

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
