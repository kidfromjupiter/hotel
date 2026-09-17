-- ============================================================
-- V3 - Calculation Functions
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_nights(
    check_in DATE,
    check_out DATE
)
RETURNS INT
LANGUAGE plpgsql
AS $$
BEGIN
    IF check_in IS NULL OR check_out IS NULL THEN
        RETURN NULL;
    END IF;

    IF check_out <= check_in THEN
        RAISE EXCEPTION
            'Check-out date (%) must be later than check-in date (%)',
            check_out,
            check_in;
    END IF;

    RETURN check_out - check_in;
END;
$$;

-- ============================================================
-- 2. calculate_room_charges
--
-- Finds the room assigned to the booking and gets its
-- daily rate from room_types.
--
-- Room charges = number of nights × daily room rate
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_room_charges(
    p_booking_id BIGINT
)
RETURNS NUMERIC(10,2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_start_date DATE;
    v_end_date DATE;
    v_daily_rate NUMERIC(10,2);
    v_nights INT;
BEGIN
    SELECT
        b.start_date,
        b.end_date,
        rt.daily_rate
    INTO
        v_start_date,
        v_end_date,
        v_daily_rate
    FROM booking b
    JOIN room_details rd
        ON rd.room_number = b.room_number
       AND rd.branch_id = b.branch_id
    JOIN room_types rt
        ON rt.room_type_id = rd.room_type_id
    WHERE b.booking_id = p_booking_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Booking % does not exist',
            p_booking_id;
    END IF;

    v_nights := calculate_nights(v_start_date, v_end_date);

    RETURN ROUND(v_nights * v_daily_rate, 2);
END;
$$;

-- ============================================================
-- 3. calculate_service_charges
--
-- Calculates the total cost of all services used by a booking.
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_service_charges(
    p_booking_id BIGINT
)
RETURNS NUMERIC(10,2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total NUMERIC(10,2);
BEGIN
    SELECT COALESCE(SUM(service_total), 0.00)
    INTO v_total
    FROM service_charges
    WHERE booking_id = p_booking_id;

    RETURN ROUND(v_total, 2);
END;
$$;

-- ============================================================
-- 4. calculate_final_bill
--
-- Calculates the final bill for a booking:
--
-- Room charges + Service charges + Tax
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_final_bill(
    p_booking_id BIGINT
)
RETURNS NUMERIC(10,2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_room_charges NUMERIC(10,2);
    v_service_charges NUMERIC(10,2);
    v_tax_percentage NUMERIC(5,2);
    v_subtotal NUMERIC(10,2);
    v_tax_amount NUMERIC(10,2);
BEGIN
    -- Calculate room charges
    v_room_charges := calculate_room_charges(p_booking_id);

    -- Calculate service charges
    v_service_charges := calculate_service_charges(p_booking_id);

    -- Get the currently active tax percentage
    SELECT tax_percentage
    INTO v_tax_percentage
    FROM tax_policies
    WHERE active = TRUE
    ORDER BY tax_id DESC
    LIMIT 1;

    -- If no active tax policy exists, use 0%
    v_tax_percentage := COALESCE(v_tax_percentage, 0.00);

    -- Calculate subtotal
    v_subtotal := v_room_charges + v_service_charges;

    -- Calculate tax
    v_tax_amount := v_subtotal * (v_tax_percentage / 100);

    -- Return final bill
    RETURN ROUND(v_subtotal + v_tax_amount, 2);
END;
$$;

-- ============================================================
-- 5. get_outstanding_balance
--
-- Calculates the amount still owed for a booking.
--
-- Outstanding balance = Grand Total - Amount Paid
-- ============================================================

CREATE OR REPLACE FUNCTION get_outstanding_balance(
    p_booking_id BIGINT
)
RETURNS NUMERIC(10,2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_grand_total NUMERIC(10,2);
    v_amount_paid NUMERIC(10,2);
BEGIN
    SELECT
        grand_total,
        amount_paid
    INTO
        v_grand_total,
        v_amount_paid
    FROM billing_summary
    WHERE booking_id = p_booking_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Billing summary for booking % does not exist',
            p_booking_id;
    END IF;

    RETURN ROUND(
        COALESCE(v_grand_total, 0.00)
        - COALESCE(v_amount_paid, 0.00),
        2
    );
END;
$$;