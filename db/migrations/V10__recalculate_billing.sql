CREATE OR REPLACE FUNCTION recalculate_billing_summary(
    p_booking_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_room_charges NUMERIC(10,2);
    v_service_charges NUMERIC(10,2);
    v_tax_percentage NUMERIC(10,2);
    v_tax_amount NUMERIC(10,2);
    v_grand_total NUMERIC(10,2);
    v_amount_paid NUMERIC(10,2);
    v_payment_status VARCHAR(50);
BEGIN
    v_room_charges := calculate_room_charges(p_booking_id);
    v_service_charges := calculate_service_charges(p_booking_id);

    SELECT tax_percentage
    INTO v_tax_percentage
    FROM tax_policies
    WHERE active = TRUE
    ORDER BY tax_id DESC
    LIMIT 1;

    v_tax_percentage := COALESCE(v_tax_percentage, 0.00);

    v_tax_amount := ROUND(
        (v_room_charges + v_service_charges)
        * (v_tax_percentage / 100),
        2
    );

    v_grand_total := ROUND(
        v_room_charges
        + v_service_charges
        + v_tax_amount,
        2
    );

    SELECT COALESCE(SUM(t.amount), 0.00)
    INTO v_amount_paid
    FROM transactions t
    JOIN billing_summary bs
        ON bs.invoice_id = t.invoice_id
    WHERE bs.booking_id = p_booking_id;

    IF v_amount_paid <= 0 THEN
        v_payment_status := 'Unpaid';
    ELSIF v_amount_paid < v_grand_total THEN
        v_payment_status := 'Partially Paid';
    ELSE
        v_payment_status := 'Paid';
    END IF;

    UPDATE billing_summary
    SET total_room_charges = v_room_charges,
        total_service_charges = v_service_charges,
        total_tax_amount = v_tax_amount,
        grand_total = v_grand_total,
        amount_paid = v_amount_paid,
        payment_status = v_payment_status
    WHERE booking_id = p_booking_id;
END;
$$;


CREATE OR REPLACE FUNCTION recalculate_after_service_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM recalculate_billing_summary(OLD.booking_id);
        RETURN OLD;
    END IF;

    IF TG_OP = 'UPDATE'
       AND OLD.booking_id IS DISTINCT FROM NEW.booking_id THEN

        PERFORM recalculate_billing_summary(OLD.booking_id);
        PERFORM recalculate_billing_summary(NEW.booking_id);

        RETURN NEW;
    END IF;

    PERFORM recalculate_billing_summary(NEW.booking_id);

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_recalculate_billing_service
AFTER INSERT OR UPDATE OR DELETE ON service_charges
FOR EACH ROW
EXECUTE FUNCTION recalculate_after_service_change();


CREATE OR REPLACE FUNCTION recalculate_after_payment()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_booking_id BIGINT;
BEGIN
    SELECT booking_id
    INTO v_booking_id
    FROM billing_summary
    WHERE invoice_id = NEW.invoice_id;

    IF v_booking_id IS NOT NULL THEN
        PERFORM recalculate_billing_summary(v_booking_id);
    END IF;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_recalculate_billing_payment
AFTER INSERT ON transactions
FOR EACH ROW
EXECUTE FUNCTION recalculate_after_payment();