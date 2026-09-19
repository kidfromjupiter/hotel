CREATE OR REPLACE FUNCTION prevent_duplicate_final_bill()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM billing_summary
        WHERE booking_id = NEW.booking_id
    ) THEN
        RAISE EXCEPTION
            'A final bill already exists for booking %',
            NEW.booking_id;
    END IF;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_prevent_duplicate_final_bill
BEFORE INSERT ON billing_summary
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_final_bill();