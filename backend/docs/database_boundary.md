# PostgreSQL and repository boundary

- PostgreSQL owns constraints and the `prevent_double_booking` trigger. It also owns multi-table write functions: `create_booking`, `add_service_to_booking`, `extend_booking_stay`, `record_invoice_payment`, and `checkout_booking`. Their related writes execute in one database transaction. Payment and checkout functions lock the booking row before the invoice row.
- Repositories own parameterized SQL for reads and single-row updates. Queries return rows; they do not build API JSON. Joins, filters, and aggregate calculations remain in PostgreSQL.
- Services map rows into API response models or dictionaries, including nested booking charges and guest payment history. The request-scoped database dependency commits successful requests and rolls back failures. A guest created during public booking creation shares that transaction with its booking and invoice.

The existing Flyway migration files now create only the retained write functions and trigger. Read queries and single-row updates live in repositories from the initial schema onward.

Because applied Flyway migrations have changed, databases that already ran the old files must be rebuilt or migrated with a separate, deliberate compatibility procedure before Flyway validation can pass.
