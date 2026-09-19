-- ============================================================
-- V9 - Service Booking Status Trigger
-- ============================================================

-- ============================================================
-- Prevent service usage for bookings that are not active.
--
-- Services are allowed only for:
-- Confirmed
-- Checked-In
--
-- Services are rejected for:
-- Pending
-- Checked-Out
-- Cancelled
-- ============================================================

CREATE OR REPLACE FUNCTION prevent_service_on_inactive_booking()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_booking_status VARCHAR(50);
BEGIN

    SELECT booking_status
    INTO v_booking_status
    FROM booking
    WHERE booking_id = NEW.booking_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Booking % does not exist',
            NEW.booking_id;
    END IF;

    IF v_booking_status NOT IN (
        'Confirmed',
        'Checked-In'
    ) THEN
        RAISE EXCEPTION
            'Cannot add service to booking % because its status is %',
            NEW.booking_id,
            v_booking_status;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_service_on_inactive_booking
BEFORE INSERT ON service_charges
FOR EACH ROW
EXECUTE FUNCTION prevent_service_on_inactive_booking();