-- V11: Add trigger to prevent double booking of a room

CREATE OR REPLACE FUNCTION check_double_booking()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.booking_status IN ('CONFIRMED', 'CHECKED_IN') THEN
    IF EXISTS (
      SELECT 1 FROM booking b
      WHERE b.room_number = NEW.room_number
        AND b.branch_id = NEW.branch_id
        AND b.booking_status IN ('CONFIRMED', 'CHECKED_IN')
        AND b.booking_id != COALESCE(NEW.booking_id, -1)
        AND b.start_date < NEW.end_date
        AND b.end_date > NEW.start_date
    ) THEN
      RAISE EXCEPTION 'Room % at branch % is already booked for the selected dates.', NEW.room_number, NEW.branch_id;
    END IF;
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS prevent_double_booking ON booking;
CREATE TRIGGER prevent_double_booking
BEFORE INSERT OR UPDATE ON booking
FOR EACH ROW
EXECUTE FUNCTION check_double_booking();
