CREATE OR REPLACE FUNCTION validate_service_date()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_start_date DATE;
    v_end_date DATE;
BEGIN
    SELECT
        start_date,
        end_date
    INTO
        v_start_date,
        v_end_date
    FROM booking
    WHERE booking_id = NEW.booking_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Booking % does not exist',
            NEW.booking_id;
    END IF;

    IF NEW.service_date IS NULL THEN
        RAISE EXCEPTION
            'Service date cannot be NULL for booking %',
            NEW.booking_id;
    END IF;

    IF NEW.service_date < v_start_date
       OR NEW.service_date >= v_end_date THEN
        RAISE EXCEPTION
            'Service date % must be within the stay from % to % for booking %',
            NEW.service_date,
            v_start_date,
            v_end_date,
            NEW.booking_id;
    END IF;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_validate_service_date
BEFORE INSERT ON service_charges
FOR EACH ROW
EXECUTE FUNCTION validate_service_date();