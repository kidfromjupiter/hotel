-- Prepare service_charges for service usage tracking.
--
-- The original service_dates INT column is being used as a quantity
-- in the existing seed data, so rename it to quantity.
--
-- Add a real service_date column for validating whether the service
-- was used during the guest's stay.
--
-- Add unit_price so the price at the time of service usage can be
-- preserved even if the catalogue price changes later.

ALTER TABLE service_charges
RENAME COLUMN service_dates TO quantity;

ALTER TABLE service_charges
ADD COLUMN service_date DATE,
ADD COLUMN unit_price NUMERIC(10,2);

ALTER TABLE service_charges
ADD CONSTRAINT chk_service_quantity_positive
    CHECK (quantity > 0);

ALTER TABLE service_charges
ADD CONSTRAINT chk_service_unit_price_nonnegative
    CHECK (unit_price >= 0);

ALTER TABLE service_charges
ADD CONSTRAINT chk_service_total_nonnegative
    CHECK (service_total >= 0);