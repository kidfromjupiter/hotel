CREATE OR REPLACE FUNCTION check_double_booking()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  IF UPPER(REPLACE(NEW.booking_status, '-', '_'))
      IN ('CONFIRMED', 'CHECKED_IN') THEN
    IF EXISTS (
      SELECT 1
      FROM booking b
      WHERE b.room_number = NEW.room_number
        AND b.branch_id = NEW.branch_id
        AND UPPER(REPLACE(b.booking_status, '-', '_'))
            IN ('CONFIRMED', 'CHECKED_IN')
        AND b.booking_id != COALESCE(NEW.booking_id, -1)
        AND b.start_date < NEW.end_date
        AND b.end_date > NEW.start_date
    ) THEN
      RAISE EXCEPTION
        'Room % at branch % is already booked for the selected dates.',
        NEW.room_number, NEW.branch_id;
    END IF;
  END IF;

  RETURN NEW;
END;
$$;
