-- ============================================================
-- V4 - Booking Triggers
-- ============================================================


-- ============================================================
-- 1. Prevent Double-Booking
--
-- Prevents two active bookings from using the same room
-- at the same branch during overlapping dates.
-- ============================================================

CREATE OR REPLACE FUNCTION prevent_double_booking()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM booking b
        WHERE b.room_number = NEW.room_number
          AND b.branch_id = NEW.branch_id
          AND b.booking_id <> NEW.booking_id
          AND b.booking_status NOT IN ('Cancelled', 'Completed')
          AND NEW.start_date < b.end_date
          AND NEW.end_date > b.start_date
    ) THEN
        RAISE EXCEPTION
            'Room % at branch % is already booked for the selected dates',
            NEW.room_number,
            NEW.branch_id;
    END IF;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_prevent_double_booking
BEFORE INSERT OR UPDATE ON booking
FOR EACH ROW
EXECUTE FUNCTION prevent_double_booking();