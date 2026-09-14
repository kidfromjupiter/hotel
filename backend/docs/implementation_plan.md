# API Design & Backend Architecture: SkyNest Hotel Management System (HRGSMS)

## Overview & Context
SkyNest Hotels operates branches in Colombo, Kandy, and Galle. The backend must handle room bookings, check-in/check-out lifecycle, chargeable guest services, tax & membership discount calculations, partial/full payments, and 5 management reports.

Following the project requirements and architectural diagram:
- **API Layer (FastAPI Routers)**: Input validation, HTTP contract, status codes, query/path parameters.
- **Service Layer (Business Logic)**: Double-booking prevention, billing calculations (discounts + taxes), room status transitions (`Available` ↔ `Occupied`), payment verification at checkout.
- **Repository Layer (Data Access)**: Database queries against PostgreSQL (clean SQL abstraction).
- **Testability & Mocking (Pytest)**: Decoupled design where Services depend on Repository interfaces and Routers depend on Services. In tests, dependencies are substituted with mocks or pretend implementations without relying on real DBs or other components.

---

## Architecture & Testability Pattern

```
┌──────────────────────────────────────────────┐
│          API Layer (FastAPI Routers)         │ ◄── Tested using TestClient + Dependency Overrides
└──────────────────────┬───────────────────────┘
                       │ Calls Service
┌──────────────────────▼───────────────────────┐
│        Service Layer (Business Logic)        │ ◄── Tested using Pytest + Mock Repositories
└──────────────────────┬───────────────────────┘
                       │ Calls Repository
┌──────────────────────▼───────────────────────┐
│       Repository Layer (Database Access)     │ ◄── SQL / Psycopg Queries
└──────────────────────────────────────────────┘
```

### Dependency Injection & Mocking Example
```python
# Service depends on abstract or protocol-based repository
class BookingService:
    def __init__(self, booking_repo: BookingRepository, room_repo: RoomRepository):
        self.booking_repo = booking_repo
        self.room_repo = room_repo

    def create_booking(self, data: BookingCreateSchema):
        # 1. Check double booking
        if self.booking_repo.has_overlapping_booking(data.room_number, data.branch_id, data.start_date, data.end_date):
            raise BookingConflictException("Room is already booked for these dates.")
        return self.booking_repo.save_booking(data)

# In Pytest (Unit Testing BookingService without touching the Database):
def test_create_booking_prevents_double_booking(mocker):
    mock_booking_repo = mocker.Mock(spec=BookingRepository)
    mock_room_repo = mocker.Mock(spec=RoomRepository)
    # Pretend repository says there IS an overlap
    mock_booking_repo.has_overlapping_booking.return_value = True

    service = BookingService(booking_repo=mock_booking_repo, room_repo=mock_room_repo)

    with pytest.raises(BookingConflictException):
        service.create_booking(sample_booking_data)
```

---

## Detailed API Endpoints Specification

### 1. Branches & Rooms (`/api/v1/branches`, `/api/v1/rooms`)
| Method | Endpoint | Description | Request Params / Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/branches` | List all branches (Colombo, Kandy, Galle) | None | `List[BranchResponse]` |
| `GET` | `/api/v1/rooms` | Search rooms with filters & date availability | Query: `branch_id`, `room_type_id`, `status`, `start_date`, `end_date` | `List[RoomDetailResponse]` |
| `GET` | `/api/v1/rooms/{branch_id}/{room_number}` | Get specific room details, amenities & daily rate | Path params | `RoomDetailResponse` |
| `PATCH` | `/api/v1/rooms/{branch_id}/{room_number}/status` | Update room status (`Available`, `Occupied`, `Maintenance`) | Body: `{ "room_status": str }` | `RoomDetailResponse` |

### 2. Guests & Memberships (`/api/v1/guests`, `/api/v1/memberships`)
| Method | Endpoint | Description | Request Params / Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/guests` | Register a new guest | Body: `{ "name": str, "national_id": str, "phone_number": int, "membership_id": Optional[int] }` | `GuestResponse` (201 Created) |
| `GET` | `/api/v1/guests` | Search guests | Query: `national_id`, `phone_number`, `name` | `List[GuestResponse]` |
| `GET` | `/api/v1/guests/{guest_id}` | Get guest profile and membership benefits | Path param: `guest_id` | `GuestDetailResponse` |
| `GET` | `/api/v1/memberships` | List membership tiers and discounts | None | `List[MembershipResponse]` |

### 3. Bookings (`/api/v1/bookings`)
| Method | Endpoint | Description | Request Params / Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/bookings` | Create a new booking (checks overlap) | Body: `BookingCreateRequest` (`room_number`, `branch_id`, `guest_id`, `start_date`, `end_date`, `adult_count`, `children_count`, `extra_amenities`) | `BookingResponse` (201 Created) |
| `GET` | `/api/v1/bookings` | List bookings | Query: `branch_id`, `guest_id`, `status`, `start_date`, `end_date` | `List[BookingResponse]` |
| `GET` | `/api/v1/bookings/{booking_id}` | Retrieve booking details, services used, billing | Path param: `booking_id` | `BookingDetailResponse` |
| `POST` | `/api/v1/bookings/{booking_id}/check-in` | Guest check-in: records `checked_in_time`, sets room to `Occupied`, booking to `Checked-In` | Path param: `booking_id`, Body: Optional `{ "check_in_time": time }` | `BookingResponse` |
| `POST` | `/api/v1/bookings/{booking_id}/check-out` | Guest check-out: validates total bill is paid! Sets room to `Available`, records `checked_out_time`, booking to `Checked-Out` | Path param: `booking_id`, Body: Optional `{ "check_out_time": time }` | `BookingResponse` (400 if unpaid dues) |
| `POST` | `/api/v1/bookings/{booking_id}/cancel` | Cancel booking | Path param: `booking_id` | `BookingResponse` |

### 4. Chargeable Guest Services (`/api/v1/services`, `/api/v1/bookings/{id}/services`)
| Method | Endpoint | Description | Request Params / Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/services` | View service catalogue (Spa, Laundry, Minibar, Room Service, etc.) | None | `List[ServiceItemResponse]` |
| `POST` | `/api/v1/bookings/{booking_id}/services` | Add service usage to an active booking | Body: `{ "service_id": int, "service_dates": int, "quantity": int }` | `ServiceChargeResponse` (201 Created) |
| `GET` | `/api/v1/bookings/{booking_id}/services` | List all service charges billed to this booking | Path param: `booking_id` | `List[ServiceChargeResponse]` |

### 5. Billing, Invoices & Payments (`/api/v1/billing`, `/api/v1/invoices`, `/api/v1/transactions`)
| Method | Endpoint | Description | Request Params / Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/bookings/{booking_id}/bill-preview` | Preview real-time bill calculation (room nights × rate, service charges, discounts, active tax policies, amount paid, balance) | Path param: `booking_id` | `BillCalculationResponse` |
| `POST` | `/api/v1/bookings/{booking_id}/invoice` | Generate final `billing_summary` invoice & snapshot taxes into `invoice_taxes` | Body: `{ "payment_method": str }` | `InvoiceResponse` (201 Created) |
| `POST` | `/api/v1/invoices/{invoice_id}/payments` | Record payment/partial payment. Updates `amount_paid`, flags status (`PAID` vs `PARTIAL`), records `transactions` entry | Body: `{ "amount": Decimal, "payment_method": str }` | `PaymentTransactionResponse` |
| `GET` | `/api/v1/invoices/{invoice_id}` | Get full invoice breakdown with tax line items and transaction history | Path param: `invoice_id` | `InvoiceDetailResponse` |

### 6. Management Reports (`/api/v1/reports`)
| Method | Endpoint | Description | Query Parameters | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/reports/occupancy` | **Report 1**: Room occupancy report for selected date or period | `branch_id`, `start_date`, `end_date` | `OccupancyReportResponse` |
| `GET` | `/api/v1/reports/guest-billing` | **Report 2**: Guest billing summary, highlighting unpaid balances & overdue flags | `payment_status`, `branch_id` | `GuestBillingReportResponse` |
| `GET` | `/api/v1/reports/service-usage` | **Report 3**: Service usage breakdown per room and service type | `branch_id`, `service_id`, `start_date`, `end_date` | `ServiceUsageReportResponse` |
| `GET` | `/api/v1/reports/monthly-revenue` | **Report 4**: Monthly revenue per branch (room charges + services) | `branch_id`, `year` | `MonthlyRevenueReportResponse` |
| `GET` | `/api/v1/reports/service-trends` | **Report 5**: Top-used services and customer preference trends | `limit`, `start_date`, `end_date` | `ServiceTrendsReportResponse` |

---

## Directory & Package Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app factory, middleware, router inclusions
│   ├── config.py                   # Environment settings & DB connection configs
│   ├── dependencies.py             # FastAPI dependency injection providers (db sessions, repos, services)
│   ├── api/                        # Layer 1: API / Routers
│   │   ├── __init__.py
│   │   ├── branches.py
│   │   ├── rooms.py
│   │   ├── guests.py
│   │   ├── bookings.py
│   │   ├── services.py
│   │   ├── billing.py
│   │   └── reports.py
│   ├── services/                   # Layer 2: Business Logic
│   │   ├── __init__.py
│   │   ├── booking_service.py      # Overlap checks, check-in/out state logic
│   │   ├── billing_service.py      # Rate calculations, discounts, taxes, checkout validation
│   │   ├── room_service.py         # Availability & status changes
│   │   ├── guest_service.py
│   │   └── report_service.py       # Aggregation queries for 5 reports
│   ├── repositories/               # Layer 3: Database Access
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract repository interface
│   │   ├── booking_repo.py
│   │   ├── room_repo.py
│   │   ├── guest_repo.py
│   │   ├── service_repo.py
│   │   ├── billing_repo.py
│   │   └── report_repo.py
│   └── schemas/                    # Pydantic Request/Response Models
│       ├── __init__.py
│       ├── booking.py
│       ├── room.py
│       ├── guest.py
│       ├── service.py
│       ├── billing.py
│       └── report.py
└── tests/                          # Pytest Suite
    ├── conftest.py                 # Fixtures, test client, mock factories
    ├── unit/                       # Pure unit tests (isolated with mocks)
    │   ├── test_booking_service.py # Tests double-booking logic, check-in/out constraints
    │   ├── test_billing_service.py # Tests rate, discount, tax, payment logic
    │   └── test_report_service.py  # Tests report calculations
    └── api/                        # API endpoint tests with mocked services
        ├── test_bookings_api.py
        ├── test_billing_api.py
        └── test_reports_api.py
```

---

## Verification & Testing Plan

### 1. Pytest Unit Testing (Zero External Dependencies)
- `tests/unit/test_booking_service.py`:
  - Verify double-booking prevention raises `409 Conflict` when dates overlap.
  - Verify check-in sets room status to `Occupied` and sets check-in timestamp.
  - Verify check-out fails if `grand_total > amount_paid` (unpaid balance error).
  - Verify check-out succeeds when fully paid and sets room status to `Available`.
- `tests/unit/test_billing_service.py`:
  - Verify room charges = `daily_rate * nights * (1 - room_discount)`.
  - Verify service charges = `sum(services) * (1 - service_discount)`.
  - Verify taxes are accurately computed based on active `tax_policies`.
  - Verify partial payments correctly compute balance and update `payment_status` to `'PARTIAL'`.
- `tests/unit/test_report_service.py`:
  - Verify aggregations for occupancy, revenue, and top-used service rankings.

### 2. Pytest API Integration / Router Testing
- Use `fastapi.testclient.TestClient`.
- Use `app.dependency_overrides` to swap real database repositories or services with mock versions.
- Test HTTP status codes (200, 201, 400, 404, 409, 422).
