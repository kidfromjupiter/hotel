CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE room_types ADD COLUMN capacity SMALLINT NOT NULL DEFAULT 2
    CHECK (capacity > 0);
ALTER TABLE room_types ADD CONSTRAINT room_type_capacity_pair UNIQUE (room_type_id, capacity);
ALTER TABLE room_types ALTER COLUMN daily_rate SET NOT NULL,
    ADD CONSTRAINT room_rate_positive CHECK (daily_rate > 0);
ALTER TABLE service_catalogue ALTER COLUMN day_rate SET NOT NULL,
    ADD CONSTRAINT service_rate_nonnegative CHECK (day_rate >= 0);
CREATE UNIQUE INDEX one_active_demo_tax ON tax_policies ((active)) WHERE active;
ALTER TABLE room_details ALTER COLUMN room_status SET NOT NULL,
    ALTER COLUMN room_type_id SET NOT NULL,
    ALTER COLUMN capacity SET NOT NULL,
    ADD CONSTRAINT room_capacity_positive CHECK (capacity > 0);
ALTER TABLE room_details ADD CONSTRAINT room_capacity_matches_type
    FOREIGN KEY (room_type_id, capacity) REFERENCES room_types(room_type_id, capacity);
ALTER TABLE booking
    ADD COLUMN nightly_rate NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (nightly_rate >= 0),
    ADD COLUMN room_discount_percentage NUMERIC(5,2) NOT NULL DEFAULT 0
        CHECK (room_discount_percentage BETWEEN 0 AND 100),
    ADD CONSTRAINT booking_dates_valid CHECK (start_date IS NOT NULL AND end_date IS NOT NULL AND end_date > start_date),
    ADD CONSTRAINT booking_guest_count_valid CHECK (adult_count >= 0 AND children_count >= 0 AND adult_count + children_count > 0),
    ADD CONSTRAINT booking_status_valid CHECK (booking_status IN ('CONFIRMED', 'CHECKED_IN', 'CHECKED_OUT', 'CANCELLED'));
ALTER TABLE booking ALTER COLUMN room_number SET NOT NULL,
    ALTER COLUMN branch_id SET NOT NULL,
    ALTER COLUMN guest_id SET NOT NULL,
    ALTER COLUMN booking_status SET NOT NULL,
    ALTER COLUMN adult_count SET NOT NULL,
    ALTER COLUMN children_count SET NOT NULL;
ALTER TABLE booking ADD CONSTRAINT booking_no_overlap
    EXCLUDE USING gist (
        branch_id WITH =, room_number WITH =,
        daterange(start_date, end_date, '[)') WITH &&
    ) WHERE (booking_status IN ('CONFIRMED', 'CHECKED_IN'));
DROP TRIGGER prevent_double_booking ON booking;
DROP FUNCTION check_double_booking();
ALTER TABLE room_details ADD CONSTRAINT room_status_valid
    CHECK (room_status IN ('AVAILABLE', 'OCCUPIED', 'MAINTENANCE'));

ALTER TABLE billing_summary
    ADD CONSTRAINT billing_one_per_booking UNIQUE (booking_id),
    ADD COLUMN tax_rate NUMERIC(5,2) NOT NULL DEFAULT 15 CHECK (tax_rate BETWEEN 0 AND 100),
    ADD CONSTRAINT billing_amounts_valid CHECK (
        total_room_charges >= 0 AND total_service_charges >= 0 AND
        total_tax_amount >= 0 AND grand_total >= 0 AND amount_paid >= 0 AND
        amount_paid <= grand_total
    ),
    ADD CONSTRAINT billing_total_matches_parts CHECK (
        grand_total = total_room_charges + total_service_charges + total_tax_amount
    );
ALTER TABLE billing_summary ALTER COLUMN booking_id SET NOT NULL,
    ALTER COLUMN total_room_charges SET NOT NULL,
    ALTER COLUMN total_service_charges SET NOT NULL,
    ALTER COLUMN total_tax_amount SET NOT NULL,
    ALTER COLUMN grand_total SET NOT NULL,
    ALTER COLUMN amount_paid SET NOT NULL,
    ALTER COLUMN payment_status SET NOT NULL;

ALTER TABLE service_charges RENAME COLUMN service_dates TO quantity;
ALTER TABLE service_charges
    ADD COLUMN usage_date DATE NOT NULL DEFAULT CURRENT_DATE,
    ADD COLUMN unit_price NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (unit_price >= 0),
    ADD COLUMN discount_percentage NUMERIC(5,2) NOT NULL DEFAULT 0
        CHECK (discount_percentage BETWEEN 0 AND 100),
    ADD CONSTRAINT service_quantity_valid CHECK (quantity > 0),
    ADD CONSTRAINT service_total_valid CHECK (service_total >= 0),
    ADD CONSTRAINT service_total_matches_price CHECK (
        service_total = ROUND(unit_price * quantity * (1 - discount_percentage / 100), 2)
    );
ALTER TABLE service_charges ALTER COLUMN booking_id SET NOT NULL,
    ALTER COLUMN service_id SET NOT NULL,
    ALTER COLUMN quantity SET NOT NULL,
    ALTER COLUMN service_total SET NOT NULL;

ALTER TABLE transactions
    ADD COLUMN room_amount NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (room_amount >= 0),
    ADD COLUMN service_amount NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (service_amount >= 0),
    ADD COLUMN tax_amount NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (tax_amount >= 0),
    ADD CONSTRAINT transaction_amount_valid CHECK (amount > 0),
    ADD CONSTRAINT transaction_allocation_valid
        CHECK (room_amount + service_amount + tax_amount = amount);
ALTER TABLE transactions ALTER COLUMN invoice_id SET NOT NULL,
    ALTER COLUMN payment_date SET NOT NULL,
    ALTER COLUMN amount SET NOT NULL,
    ALTER COLUMN payment_method SET NOT NULL;

CREATE INDEX idx_transactions_payment_date ON transactions (payment_date);
CREATE INDEX idx_transactions_invoice_id ON transactions (invoice_id);
CREATE INDEX idx_service_charges_usage_date_service ON service_charges (usage_date, service_id);

CREATE OR REPLACE FUNCTION validate_booking_capacity()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE v_capacity SMALLINT;
BEGIN
    SELECT capacity INTO v_capacity FROM room_details
    WHERE branch_id = NEW.branch_id AND room_number = NEW.room_number;
    IF v_capacity IS NOT NULL AND NEW.adult_count + NEW.children_count > v_capacity THEN
        RAISE EXCEPTION 'Guest count exceeds room capacity';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER booking_capacity BEFORE INSERT OR UPDATE OF room_number, branch_id, adult_count, children_count
ON booking FOR EACH ROW EXECUTE FUNCTION validate_booking_capacity();

CREATE OR REPLACE FUNCTION check_in_booking(p_booking_id BIGINT, p_time TIME DEFAULT CURRENT_TIME)
RETURNS BOOLEAN LANGUAGE plpgsql AS $$
DECLARE v_room SMALLINT; v_branch INT; v_status TEXT;
BEGIN
    SELECT room_number, branch_id, booking_status INTO v_room, v_branch, v_status
    FROM booking WHERE booking_id = p_booking_id FOR UPDATE;
    IF NOT FOUND OR v_status <> 'CONFIRMED' THEN RETURN FALSE; END IF;
    PERFORM 1 FROM room_details WHERE room_number = v_room AND branch_id = v_branch
        AND room_status = 'AVAILABLE' FOR UPDATE;
    IF NOT FOUND THEN RETURN FALSE; END IF;
    UPDATE booking SET booking_status = 'CHECKED_IN', checked_in_time = p_time
    WHERE booking_id = p_booking_id;
    UPDATE room_details SET room_status = 'OCCUPIED'
    WHERE room_number = v_room AND branch_id = v_branch;
    RETURN TRUE;
END;
$$;

CREATE OR REPLACE FUNCTION recalculate_booking_bill(p_booking_id BIGINT)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE v_room NUMERIC(10,2); v_services NUMERIC(10,2); v_tax NUMERIC(10,2);
        v_rate NUMERIC(5,2); v_paid NUMERIC(10,2); v_invoice UUID;
BEGIN
    SELECT ROUND((b.end_date - b.start_date) * b.nightly_rate *
                 (1 - b.room_discount_percentage / 100), 2)
    INTO v_room FROM booking b WHERE b.booking_id = p_booking_id FOR UPDATE;
    SELECT invoice_id, tax_rate, COALESCE(amount_paid, 0) INTO v_invoice, v_rate, v_paid
    FROM billing_summary WHERE booking_id = p_booking_id FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'Invoice missing for booking %', p_booking_id; END IF;
    SELECT COALESCE(SUM(service_total), 0) INTO v_services
    FROM service_charges WHERE booking_id = p_booking_id;
    v_tax := ROUND((v_room + v_services) * v_rate / 100, 2);
    IF v_paid > v_room + v_services + v_tax THEN
        RAISE EXCEPTION 'Bill cannot fall below payments already received';
    END IF;
    UPDATE billing_summary SET total_room_charges = v_room,
        total_service_charges = v_services, total_tax_amount = v_tax,
        grand_total = v_room + v_services + v_tax,
        payment_status = CASE WHEN v_paid = v_room + v_services + v_tax THEN 'PAID'
                              WHEN v_paid > 0 THEN 'PARTIALLY_PAID' ELSE 'UNPAID' END
    WHERE invoice_id = v_invoice;
    UPDATE invoice_taxes SET calculated_amount = v_tax WHERE invoice_id = v_invoice;
END;
$$;

CREATE OR REPLACE FUNCTION room_availability(p_start DATE, p_end DATE)
RETURNS TABLE(branch_id INT, room_number SMALLINT, stay_date DATE, available BOOLEAN)
LANGUAGE plpgsql STABLE AS $$
BEGIN
    IF p_end <= p_start THEN RAISE EXCEPTION 'End date must be after start date'; END IF;
    RETURN QUERY
    SELECT r.branch_id, r.room_number, d.day::DATE,
           r.room_status <> 'MAINTENANCE' AND NOT EXISTS (
               SELECT 1 FROM booking b WHERE b.branch_id = r.branch_id
                 AND b.room_number = r.room_number
                 AND b.booking_status IN ('CONFIRMED', 'CHECKED_IN')
                 AND b.start_date <= d.day::DATE AND b.end_date > d.day::DATE)
    FROM room_details r CROSS JOIN generate_series(p_start, p_end - 1, INTERVAL '1 day') d(day);
END;
$$;
