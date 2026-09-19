-- ============================================================
-- V5 - Booking Status Triggers
-- ============================================================


-- ============================================================
-- 1. Correct Double-Booking Logic
--
-- Active bookings:
-- Pending
-- Confirmed
-- Checked-In
--
-- Inactive bookings:
-- Checked-Out
-- Cancelled
--
-- This replaces the double-booking function created in V4.
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
          AND b.booking_status IN (
              'Pending',
              'Confirmed',
              'Checked-In'
          )
          AND NEW.booking_status IN (
              'Pending',
              'Confirmed',
              'Checked-In'
          )
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


-- ============================================================
-- 2. Validate Booking Status Transitions
--
-- Allowed:
--
-- Pending    -> Confirmed, Cancelled
-- Confirmed  -> Checked-In, Cancelled
-- Checked-In -> Checked-Out
--
-- Checked-Out and Cancelled are final states.
-- ============================================================

CREATE OR REPLACE FUNCTION validate_booking_status_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    -- Make sure the new status is valid.
    IF NEW.booking_status NOT IN (
        'Pending',
        'Confirmed',
        'Checked-In',
        'Checked-Out',
        'Cancelled'
    ) THEN
        RAISE EXCEPTION
            'Invalid booking status: %',
            NEW.booking_status;
    END IF;


    -- No status change.
    IF OLD.booking_status = NEW.booking_status THEN
        RETURN NEW;
    END IF;


    -- Pending -> Confirmed or Cancelled
    IF OLD.booking_status = 'Pending' THEN
        IF NEW.booking_status IN ('Confirmed', 'Cancelled') THEN
            RETURN NEW;
        END IF;

        RAISE EXCEPTION
            'Invalid booking status transition: % -> %',
            OLD.booking_status,
            NEW.booking_status;
    END IF;


    -- Confirmed -> Checked-In or Cancelled
    IF OLD.booking_status = 'Confirmed' THEN
        IF NEW.booking_status IN ('Checked-In', 'Cancelled') THEN
            RETURN NEW;
        END IF;

        RAISE EXCEPTION
            'Invalid booking status transition: % -> %',
            OLD.booking_status,
            NEW.booking_status;
    END IF;


    -- Checked-In -> Checked-Out
    IF OLD.booking_status = 'Checked-In' THEN
        IF NEW.booking_status = 'Checked-Out' THEN
            RETURN NEW;
        END IF;

        RAISE EXCEPTION
            'Invalid booking status transition: % -> %',
            OLD.booking_status,
            NEW.booking_status;
    END IF;


    -- Checked-Out and Cancelled cannot change.
    RAISE EXCEPTION
        'Invalid booking status transition: % -> %',
        OLD.booking_status,
        NEW.booking_status;

END;
$$;


CREATE TRIGGER trg_validate_booking_status_transition
BEFORE UPDATE OF booking_status ON booking
FOR EACH ROW
EXECUTE FUNCTION validate_booking_status_transition();