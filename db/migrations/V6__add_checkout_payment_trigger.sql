-- ============================================================
-- V6 - Checkout Payment Trigger
-- ============================================================


-- ============================================================
-- 1. Block Checkout While Unpaid
--
-- A booking can only move to Checked-Out when the amount paid
-- is greater than or equal to the grand total.
--
-- If no billing summary exists, checkout is rejected.
-- ============================================================

CREATE OR REPLACE FUNCTION prevent_unpaid_checkout()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_grand_total NUMERIC(10,2);
    v_amount_paid NUMERIC(10,2);
BEGIN

    -- Only check payment when the booking is being checked out.
    IF NEW.booking_status = 'Checked-Out'
       AND OLD.booking_status <> 'Checked-Out' THEN

        SELECT
            grand_total,
            amount_paid
        INTO
            v_grand_total,
            v_amount_paid
        FROM billing_summary
        WHERE booking_id = NEW.booking_id;

        -- A billing summary must exist before checkout.
        IF NOT FOUND THEN
            RAISE EXCEPTION
                'Cannot check out booking % because no billing summary exists',
                NEW.booking_id;
        END IF;

        -- Treat NULL payment as zero.
        v_amount_paid := COALESCE(v_amount_paid, 0.00);
        v_grand_total := COALESCE(v_grand_total, 0.00);

        -- Reject checkout if the bill is not fully paid.
        IF v_amount_paid < v_grand_total THEN
            RAISE EXCEPTION
                'Cannot check out booking % because the bill is unpaid. Grand total: %, Amount paid: %',
                NEW.booking_id,
                v_grand_total,
                v_amount_paid;
        END IF;

    END IF;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_prevent_unpaid_checkout
BEFORE UPDATE OF booking_status ON booking
FOR EACH ROW
EXECUTE FUNCTION prevent_unpaid_checkout();