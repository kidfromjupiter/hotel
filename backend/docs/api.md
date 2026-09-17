# SkyNest Hotels — Backend API Documentation

> **Base URL:** `/api/v1`  
> **Framework:** FastAPI (Python)  
> **Auth:** _To be defined (JWT planned)_

---

## Table of Contents

1. [Branches](#1-branches)
2. [Rooms](#2-rooms)
3. [Guests & Memberships](#3-guests--memberships)
4. [Bookings](#4-bookings)
5. [Guest Services](#5-guest-services)
6. [Billing & Invoices](#6-billing--invoices)
7. [Management Reports](#7-management-reports)

---

## 1. Branches

### `GET /branches/`

List all hotel branches.

**Request**
- No body, no query parameters.

**Response** `200 OK`
```json
[
  { "branch_id": 1, "branch_name": "Colombo" },
  { "branch_id": 2, "branch_name": "Kandy" },
  { "branch_id": 3, "branch_name": "Galle" }
]
```

**Business Logic**
- Returns a static list of SkyNest hotel branches.

---

## 2. Rooms

### `GET /rooms/`

Search and filter available rooms.

**Request — Query Parameters**

| Parameter     | Type     | Required | Description                                    |
| :------------ | :------- | :------: | :--------------------------------------------- |
| `branch_id`   | `int`    | No       | Filter by branch                               |
| `room_type_id`| `string` | No       | Filter by room type (`SINGLE`, `STANDARD`, `DELUXE`, `FAMILY`, `FAMILY_DELUXE`) |
| `status`      | `string` | No       | Filter by room status (`Available`, `Occupied`, `Maintenance`) |
| `start_date`  | `date`   | No       | Start of availability window (`YYYY-MM-DD`)    |
| `end_date`    | `date`   | No       | End of availability window (`YYYY-MM-DD`)      |

**Response** `200 OK`
```json
[
  {
    "room_number": 101,
    "branch_id": 1,
    "branch_name": "Colombo",
    "room_type_id": "STANDARD",
    "room_status": "Available",
    "daily_rate": 150.00,
    "capacity": 2,
    "amenities": ["Wi-Fi", "AC", "TV"]
  }
]
```

**Business Logic**
- If `start_date` and `end_date` are provided, excludes rooms that have a booking with `Checked-In` or `Confirmed` status that overlaps those dates.
- Applies all active filters independently (branch, type, status).

---

### `GET /rooms/{branch_id}/{room_number}`

Get details of a specific room.

**Request — Path Parameters**

| Parameter     | Type      | Description        |
| :------------ | :-------- | :----------------- |
| `branch_id`   | `int`     | Branch identifier  |
| `room_number` | `int`     | Room number        |

**Response** `200 OK`
```json
{
  "room_number": 101,
  "branch_id": 1,
  "branch_name": "Colombo",
  "room_type_id": "DELUXE",
  "room_status": "Available",
  "daily_rate": 220.00,
  "capacity": 2,
  "amenities": ["Wi-Fi", "AC", "TV", "Balcony", "Mini-Fridge", "Coffee Maker", "Bathrobe"]
}
```

**Error Responses**
- `404 Not Found` — Room does not exist.

**Business Logic**
- Fetches room details and joins the room type's amenities from the `room_amenities` table.

---

### `PATCH /rooms/{branch_id}/{room_number}/status`

Manually update a room's status (e.g. flag for maintenance).

**Request — Path Parameters**

| Parameter     | Type  | Description   |
| :------------ | :---- | :------------ |
| `branch_id`   | `int` | Branch ID     |
| `room_number` | `int` | Room number   |

**Request Body**
```json
{ "room_status": "Maintenance" }
```

| Field         | Type     | Values                                  |
| :------------ | :------- | :-------------------------------------- |
| `room_status` | `string` | `Available`, `Occupied`, `Maintenance`  |

**Response** `200 OK`
```json
{
  "room_number": 101,
  "branch_id": 1,
  "room_status": "Maintenance"
}
```

**Error Responses**
- `400 Bad Request` — Invalid status value.
- `404 Not Found` — Room does not exist.

**Business Logic**
- Does not allow setting status to `Occupied` manually — that is handled automatically by the check-in process.
- Rooms set to `Maintenance` are excluded from availability searches.

---

## 3. Guests & Memberships

### `POST /guests/`

Register a new guest.

**Request Body**
```json
{
  "name": "Amal Perera",
  "national_id": "987654321V",
  "phone_number": 771234567,
  "membership_id": 2
}
```

| Field           | Type      | Required | Description                              |
| :-------------- | :-------- | :------: | :--------------------------------------- |
| `name`          | `string`  | Yes      | Full name of the guest                   |
| `national_id`   | `string`  | Yes      | National ID / Passport number            |
| `phone_number`  | `int`     | Yes      | Contact number                           |
| `membership_id` | `int`     | No       | SkyNest membership tier ID (optional)   |

**Response** `201 Created`
```json
{
  "guest_id": 1001,
  "name": "Amal Perera",
  "national_id": "987654321V",
  "phone_number": 771234567,
  "membership_id": 2,
  "membership_name": "Gold"
}
```

**Error Responses**
- `409 Conflict` — A guest with this `national_id` already exists.
- `422 Unprocessable Entity` — Validation errors (missing required fields).

**Business Logic**
- Checks for duplicate `national_id` before saving.
- If `membership_id` is not provided, the guest is registered with no membership (standard rates apply).

---

### `GET /guests/`

Search guests.

**Request — Query Parameters**

| Parameter       | Type     | Required | Description              |
| :-------------- | :------- | :------: | :----------------------- |
| `national_id`   | `string` | No       | Exact match search       |
| `phone_number`  | `int`    | No       | Exact match search       |
| `name`          | `string` | No       | Partial / case-insensitive search |

**Response** `200 OK`
```json
[
  {
    "guest_id": 1001,
    "name": "Amal Perera",
    "national_id": "987654321V",
    "phone_number": 771234567,
    "membership_name": "Gold"
  }
]
```

**Business Logic**
- At least one search parameter should be provided; returns all guests otherwise.
- Name search is case-insensitive partial match (`ILIKE`).

---

### `GET /guests/{guest_id}`

Get a guest's full profile.

**Request — Path Parameters**

| Parameter  | Type  | Description     |
| :--------- | :---- | :-------------- |
| `guest_id` | `int` | Guest ID        |

**Response** `200 OK`
```json
{
  "guest_id": 1001,
  "name": "Amal Perera",
  "national_id": "987654321V",
  "phone_number": 771234567,
  "membership": {
    "membership_id": 2,
    "membership_name": "Gold",
    "room_discount_percentage": 10.00,
    "service_discount_percentage": 5.00
  }
}
```

**Error Responses**
- `404 Not Found` — Guest does not exist.

---

### `GET /memberships/`

List all SkyNest membership tiers and their discount rates.

> **Note:** Route prefix is `/api/v1/memberships` (separate from `/guests`).

**Request**
- No body, no parameters.

**Response** `200 OK`
```json
[
  {
    "membership_id": 1,
    "membership_name": "Silver",
    "room_discount_percentage": 5.00,
    "service_discount_percentage": 2.50
  },
  {
    "membership_id": 2,
    "membership_name": "Gold",
    "room_discount_percentage": 10.00,
    "service_discount_percentage": 5.00
  }
]
```

---

## 4. Bookings

### `POST /bookings/`

Create a new room booking.

**Request Body**
```json
{
  "room_number": 101,
  "branch_id": 1,
  "guest_id": 1001,
  "start_date": "2026-10-01",
  "end_date": "2026-10-05",
  "adult_count": 2,
  "children_count": 0,
  "extra_amenities": [
    { "amenity_id": 3, "quantity": 2 }
  ]
}
```

| Field             | Type         | Required | Description                                    |
| :---------------- | :----------- | :------: | :--------------------------------------------- |
| `room_number`     | `int`        | Yes      | Room to book                                   |
| `branch_id`       | `int`        | Yes      | Branch of the room                             |
| `guest_id`        | `int`        | Yes      | Guest making the booking                       |
| `start_date`      | `date`       | Yes      | Check-in date (`YYYY-MM-DD`)                   |
| `end_date`        | `date`       | Yes      | Check-out date (`YYYY-MM-DD`)                  |
| `adult_count`     | `int`        | Yes      | Number of adults                               |
| `children_count`  | `int`        | Yes      | Number of children                             |
| `extra_amenities` | `array`      | No       | Additional amenities requested                 |

**Response** `201 Created`
```json
{
  "booking_id": 500001,
  "room_number": 101,
  "branch_id": 1,
  "guest_id": 1001,
  "booking_status": "Confirmed",
  "start_date": "2026-10-01",
  "end_date": "2026-10-05",
  "adult_count": 2,
  "children_count": 0
}
```

**Error Responses**
- `400 Bad Request` — `end_date` is before or equal to `start_date`.
- `409 Conflict` — The room is already booked for overlapping dates.
- `422 Unprocessable Entity` — Total guests exceed room type capacity.
- `404 Not Found` — Guest or room does not exist.

**Business Logic**
- Checks for any overlapping booking on the same `room_number` + `branch_id` pair (status `Confirmed` or `Checked-In`).
- Validates total guests (`adult_count + children_count`) does not exceed room capacity:
  - `SINGLE` → max 1 person
  - `STANDARD` / `DELUXE` → max 2 people
  - `FAMILY` / `FAMILY_DELUXE` → max 5 people
- Sets initial `booking_status` to `Confirmed`.
- Saves any extra amenities requested into `booking_extra_amenities`.

---

### `GET /bookings/`

List and filter bookings.

**Request — Query Parameters**

| Parameter    | Type     | Required | Description                      |
| :----------- | :------- | :------: | :------------------------------- |
| `branch_id`  | `int`    | No       | Filter by branch                 |
| `guest_id`   | `int`    | No       | Filter by guest                  |
| `status`     | `string` | No       | Filter by booking status         |
| `start_date` | `date`   | No       | Filter bookings starting from    |
| `end_date`   | `date`   | No       | Filter bookings ending before    |

**Response** `200 OK`
```json
[
  {
    "booking_id": 500001,
    "guest_name": "Amal Perera",
    "room_number": 101,
    "branch_name": "Colombo",
    "booking_status": "Confirmed",
    "start_date": "2026-10-01",
    "end_date": "2026-10-05"
  }
]
```

---

### `GET /bookings/{booking_id}`

Get full booking details including services and billing status.

**Response** `200 OK`
```json
{
  "booking_id": 500001,
  "guest": { "guest_id": 1001, "name": "Amal Perera" },
  "room": { "room_number": 101, "branch_name": "Colombo", "room_type_id": "STANDARD" },
  "booking_status": "Checked-In",
  "start_date": "2026-10-01",
  "end_date": "2026-10-05",
  "checked_in_time": "14:00:00",
  "checked_out_time": null,
  "adult_count": 2,
  "children_count": 0,
  "service_charges": [
    { "service_name": "Spa", "service_dates": 2, "service_total": 80.00 }
  ],
  "invoice_status": "PARTIAL"
}
```

---

### `POST /bookings/{booking_id}/check-in`

Check a guest in.

**Request Body** _(optional)_
```json
{ "check_in_time": "14:30:00" }
```

**Response** `200 OK`
```json
{
  "booking_id": 500001,
  "booking_status": "Checked-In",
  "checked_in_time": "14:30:00"
}
```

**Error Responses**
- `400 Bad Request` — Booking is not in `Confirmed` status.
- `404 Not Found` — Booking does not exist.

**Business Logic**
- Sets `booking_status` → `Checked-In`.
- Sets `checked_in_time` to provided time or server's current time.
- Sets `room_status` → `Occupied`.

---

### `POST /bookings/{booking_id}/check-out`

Check a guest out.

**Request Body** _(optional)_
```json
{ "check_out_time": "11:00:00" }
```

**Response** `200 OK`
```json
{
  "booking_id": 500001,
  "booking_status": "Checked-Out",
  "checked_out_time": "11:00:00"
}
```

**Error Responses**
- `400 Bad Request` — Outstanding unpaid balance exists (`grand_total > amount_paid`).
- `400 Bad Request` — Booking is not in `Checked-In` status.
- `404 Not Found` — Booking does not exist.

**Business Logic**
- **Enforces full payment before checkout** — if any unpaid balance remains, checkout is blocked and the outstanding amount is returned in the error message.
- Sets `booking_status` → `Checked-Out`.
- Sets `checked_out_time` to provided time or server's current time.
- Sets `room_status` → `Available`.

---

### `POST /bookings/{booking_id}/cancel`

Cancel a booking.

**Response** `200 OK`
```json
{ "booking_id": 500001, "booking_status": "Cancelled" }
```

**Error Responses**
- `400 Bad Request` — Cannot cancel a booking that is already `Checked-In` or `Checked-Out`.

**Business Logic**
- Sets `booking_status` → `Cancelled`.
- If room was held, sets `room_status` back to `Available`.

---

## 5. Guest Services

### `GET /services/`

List the full service catalogue.

**Response** `200 OK`
```json
[
  { "service_id": 1, "service_name": "Spa Treatment", "day_rate": 40.00 },
  { "service_id": 2, "service_name": "Laundry",       "day_rate": 15.00 },
  { "service_id": 3, "service_name": "Room Service",  "day_rate": 25.00 },
  { "service_id": 4, "service_name": "Minibar",       "day_rate": 20.00 }
]
```

---

### `POST /bookings/{booking_id}/services`

Log a service charge against an active booking.

**Request Body**
```json
{
  "service_id": 1,
  "service_dates": 2
}
```

| Field           | Type  | Required | Description                                             |
| :-------------- | :---- | :------: | :------------------------------------------------------ |
| `service_id`    | `int` | Yes      | ID of the service from the catalogue                    |
| `service_dates` | `int` | Yes      | Number of days / sessions the service was used          |

**Response** `201 Created`
```json
{
  "service_log_id": 301,
  "booking_id": 500001,
  "service_name": "Spa Treatment",
  "service_dates": 2,
  "service_total": 80.00
}
```

**Error Responses**
- `400 Bad Request` — Booking is not in `Checked-In` status.
- `404 Not Found` — Service or booking does not exist.

**Business Logic**
- `service_total` is calculated as `day_rate × service_dates`.
- The service total snapshot is stored at time of logging (even if `day_rate` changes later).
- Can only add services to bookings in `Checked-In` status.

---

### `GET /bookings/{booking_id}/services`

List all service charges billed to a booking.

**Response** `200 OK`
```json
[
  { "service_log_id": 301, "service_name": "Spa Treatment", "service_dates": 2, "service_total": 80.00 },
  { "service_log_id": 302, "service_name": "Laundry",       "service_dates": 3, "service_total": 45.00 }
]
```

---

## 6. Billing & Invoices

### `GET /bookings/{booking_id}/bill-preview`

Get a live real-time bill calculation before generating a formal invoice.

**Response** `200 OK`
```json
{
  "booking_id": 500001,
  "room_type": "STANDARD",
  "nights": 4,
  "daily_rate": 150.00,
  "room_charges_before_discount": 600.00,
  "room_discount_percentage": 10.00,
  "total_room_charges": 540.00,
  "total_service_charges_before_discount": 125.00,
  "service_discount_percentage": 5.00,
  "total_service_charges": 118.75,
  "active_taxes": [
    { "tax_name": "VAT", "tax_percentage": 15.00, "calculated_amount": 98.81 }
  ],
  "total_tax_amount": 98.81,
  "grand_total": 757.56,
  "amount_paid": 200.00,
  "outstanding_balance": 557.56,
  "payment_status": "PARTIAL"
}
```

**Business Logic**
- `nights` = `end_date - start_date` (number of days).
- Room charges = `daily_rate × nights`.
- Membership room discount applied: `room_charges × (1 - room_discount_percentage / 100)`.
- Membership service discount applied: `sum(service_charges) × (1 - service_discount_percentage / 100)`.
- Taxes applied from all **active** records in `tax_policies` table (e.g. VAT, service tax).
- `amount_paid` is summed from all transactions against the booking's invoice.

---

### `POST /bookings/{booking_id}/invoice`

Generate the official invoice for a booking. Snapshots the current tax rates.

**Request Body**
```json
{ "payment_method": "Card" }
```

| Field            | Type     | Values                              |
| :--------------- | :------- | :---------------------------------- |
| `payment_method` | `string` | `Card`, `Cash`, `Bank Transfer`     |

**Response** `201 Created`
```json
{
  "invoice_id": "550e8400-e29b-41d4-a716-446655440000",
  "booking_id": 500001,
  "payment_method": "Card",
  "total_room_charges": 540.00,
  "total_service_charges": 118.75,
  "total_tax_amount": 98.81,
  "grand_total": 757.56,
  "amount_paid": 0.00,
  "payment_status": "UNPAID"
}
```

**Error Responses**
- `409 Conflict` — An invoice already exists for this booking.
- `404 Not Found` — Booking does not exist.

**Business Logic**
- Freezes the current tax rates into `invoice_taxes` table (tax policy changes after invoice generation won't affect this bill).
- Sets `payment_status` to `UNPAID` initially.
- Should only be called once per booking.

---

### `POST /invoices/{invoice_id}/payments`

Record a payment (full or partial) against an invoice.

**Request Body**
```json
{
  "amount": 300.00,
  "payment_method": "Cash"
}
```

| Field            | Type      | Required | Description              |
| :--------------- | :-------- | :------: | :----------------------- |
| `amount`         | `decimal` | Yes      | Amount being paid now    |
| `payment_method` | `string`  | Yes      | `Card`, `Cash`, `Bank Transfer` |

**Response** `201 Created`
```json
{
  "transaction_id": "uuid-here",
  "invoice_id": "550e8400-...",
  "payment_date": "2026-10-05T11:00:00",
  "amount": 300.00,
  "new_amount_paid": 300.00,
  "outstanding_balance": 457.56,
  "payment_status": "PARTIAL"
}
```

**Error Responses**
- `400 Bad Request` — Payment amount exceeds outstanding balance.
- `404 Not Found` — Invoice does not exist.

**Business Logic**
- Creates a new record in the `transactions` table.
- Updates `amount_paid` in `billing_summary`.
- If `amount_paid >= grand_total`, sets `payment_status` → `PAID`.
- If `amount_paid > 0` but less than `grand_total`, sets `payment_status` → `PARTIAL`.

---

### `GET /invoices/{invoice_id}`

Get the full invoice details with tax breakdown and transaction history.

**Response** `200 OK`
```json
{
  "invoice_id": "550e8400-...",
  "booking_id": 500001,
  "payment_method": "Card",
  "total_room_charges": 540.00,
  "total_service_charges": 118.75,
  "total_tax_amount": 98.81,
  "grand_total": 757.56,
  "amount_paid": 757.56,
  "payment_status": "PAID",
  "taxes": [
    { "tax_name": "VAT", "tax_percentage": 15.00, "calculated_amount": 98.81 }
  ],
  "transactions": [
    {
      "transaction_id": "uuid-1",
      "payment_date": "2026-10-03T14:00:00",
      "amount": 300.00,
      "payment_method": "Card"
    },
    {
      "transaction_id": "uuid-2",
      "payment_date": "2026-10-05T11:00:00",
      "amount": 457.56,
      "payment_method": "Cash"
    }
  ]
}
```

---

## 7. Management Reports

### `GET /reports/occupancy`

**Report 1** — Room occupancy rate for a selected period.

**Query Parameters**

| Parameter    | Type   | Required | Description               |
| :----------- | :----- | :------: | :------------------------ |
| `branch_id`  | `int`  | No       | Filter by branch          |
| `start_date` | `date` | Yes      | Period start              |
| `end_date`   | `date` | Yes      | Period end                |

**Response** `200 OK`
```json
{
  "period": { "start_date": "2026-10-01", "end_date": "2026-10-31" },
  "branches": [
    {
      "branch_name": "Colombo",
      "total_rooms": 20,
      "occupied_nights": 180,
      "total_possible_nights": 620,
      "occupancy_rate_percent": 29.03
    }
  ]
}
```

**Business Logic**
- `occupancy_rate` = `occupied_nights / (total_rooms × period_days) × 100`
- Counts `Checked-In` and `Checked-Out` bookings overlapping the selected period.

---

### `GET /reports/guest-billing`

**Report 2** — Guest billing summary, flagging unpaid balances.

**Query Parameters**

| Parameter        | Type     | Required | Description                         |
| :--------------- | :------- | :------: | :---------------------------------- |
| `payment_status` | `string` | No       | `PAID`, `PARTIAL`, `UNPAID`         |
| `branch_id`      | `int`    | No       | Filter by branch                    |

**Response** `200 OK`
```json
{
  "data": [
    {
      "guest_name": "Amal Perera",
      "booking_id": 500001,
      "grand_total": 757.56,
      "amount_paid": 300.00,
      "outstanding_balance": 457.56,
      "payment_status": "PARTIAL",
      "is_overdue": true
    }
  ]
}
```

**Business Logic**
- `is_overdue` = `True` if `payment_status != PAID` and the booking's `end_date` has already passed.

---

### `GET /reports/service-usage`

**Report 3** — Service usage breakdown per room and service type.

**Query Parameters**

| Parameter    | Type   | Required | Description                       |
| :----------- | :----- | :------: | :-------------------------------- |
| `branch_id`  | `int`  | No       | Filter by branch                  |
| `service_id` | `int`  | No       | Filter by specific service        |
| `start_date` | `date` | No       | Period start                      |
| `end_date`   | `date` | No       | Period end                        |

**Response** `200 OK`
```json
{
  "data": [
    {
      "service_name": "Spa Treatment",
      "total_bookings_used": 42,
      "total_days_used": 89,
      "total_revenue": 3560.00
    }
  ]
}
```

---

### `GET /reports/monthly-revenue`

**Report 4** — Monthly revenue breakdown by branch.

**Query Parameters**

| Parameter   | Type  | Required | Description            |
| :---------- | :---- | :------: | :--------------------- |
| `branch_id` | `int` | No       | Filter by branch       |
| `year`      | `int` | Yes      | Year to report on      |

**Response** `200 OK`
```json
{
  "year": 2026,
  "data": [
    {
      "branch_name": "Colombo",
      "month": "October",
      "room_revenue": 12500.00,
      "service_revenue": 3200.00,
      "total_revenue": 15700.00
    }
  ]
}
```

---

### `GET /reports/service-trends`

**Report 5** — Top-used services and customer preference trends.

**Query Parameters**

| Parameter    | Type   | Required | Description                    |
| :----------- | :----- | :------: | :----------------------------- |
| `limit`      | `int`  | No       | Number of top services (default: 5) |
| `start_date` | `date` | No       | Period start                   |
| `end_date`   | `date` | No       | Period end                     |

**Response** `200 OK`
```json
{
  "period": { "start_date": "2026-01-01", "end_date": "2026-12-31" },
  "top_services": [
    { "rank": 1, "service_name": "Room Service",  "times_used": 312, "total_revenue": 7800.00 },
    { "rank": 2, "service_name": "Spa Treatment", "times_used": 189, "total_revenue": 7560.00 },
    { "rank": 3, "service_name": "Laundry",       "times_used": 145, "total_revenue": 2175.00 }
  ]
}
```

**Business Logic**
- Ranks services by `times_used` (count of `service_charges` records) descending.
- `limit` caps the number of results returned.

---

## Room Type Reference

| Room Type ID    | Display Name       | Beds           | Max Capacity |
| :-------------- | :----------------- | :------------- | :----------: |
| `SINGLE`        | Single Room        | 1 Bed          | **1**        |
| `STANDARD`      | Standard Room      | 1 Large Bed    | **2**        |
| `DELUXE`        | Deluxe Room        | 1 Large Bed    | **2**        |
| `FAMILY`        | Family Room        | 2 Large Beds   | **5**        |
| `FAMILY_DELUXE` | Deluxe Family Room | 2 Large Beds   | **5**        |

> `DELUXE` shares the same bed config as `STANDARD` but includes additional amenities.  
> `FAMILY_DELUXE` shares the same bed config as `FAMILY` but includes additional amenities.
