CREATE OR REPLACE FUNCTION prevent_guest_delete()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM booking
        WHERE guest_id = OLD.guest_id
    ) THEN
        RAISE EXCEPTION
            'Cannot delete guest % because existing bookings reference this guest',
            OLD.guest_id;
    END IF;

    RETURN OLD;
END;
$$;


CREATE TRIGGER trg_prevent_guest_delete
BEFORE DELETE ON guests
FOR EACH ROW
EXECUTE FUNCTION prevent_guest_delete();


CREATE OR REPLACE FUNCTION prevent_room_delete()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM booking
        WHERE room_number = OLD.room_number
          AND branch_id = OLD.branch_id
    ) THEN
        RAISE EXCEPTION
            'Cannot delete room % at branch % because existing bookings reference this room',
            OLD.room_number,
            OLD.branch_id;
    END IF;

    RETURN OLD;
END;
$$;


CREATE TRIGGER trg_prevent_room_delete
BEFORE DELETE ON room_details
FOR EACH ROW
EXECUTE FUNCTION prevent_room_delete();


CREATE OR REPLACE FUNCTION prevent_booking_delete()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM billing_summary
        WHERE booking_id = OLD.booking_id
    ) THEN
        RAISE EXCEPTION
            'Cannot delete booking % because a billing summary exists',
            OLD.booking_id;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM booking_extra_amenities
        WHERE booking_id = OLD.booking_id
    ) THEN
        RAISE EXCEPTION
            'Cannot delete booking % because booking amenities exist',
            OLD.booking_id;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM service_charges
        WHERE booking_id = OLD.booking_id
    ) THEN
        RAISE EXCEPTION
            'Cannot delete booking % because service charges exist',
            OLD.booking_id;
    END IF;

    RETURN OLD;
END;
$$;


CREATE TRIGGER trg_prevent_booking_delete
BEFORE DELETE ON booking
FOR EACH ROW
EXECUTE FUNCTION prevent_booking_delete();


CREATE OR REPLACE FUNCTION prevent_service_delete()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM service_charges
        WHERE service_id = OLD.service_id
    ) THEN
        RAISE EXCEPTION
            'Cannot delete service % because existing service charges reference it',
            OLD.service_id;
    END IF;

    RETURN OLD;
END;
$$;


CREATE TRIGGER trg_prevent_service_delete
BEFORE DELETE ON service_catalogue
FOR EACH ROW
EXECUTE FUNCTION prevent_service_delete();