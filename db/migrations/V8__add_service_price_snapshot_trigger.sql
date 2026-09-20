-- ============================================================
-- V8 - Service Price Snapshot Trigger
-- ============================================================

-- ============================================================
-- Snapshot the service price when a service is used.
--
-- service_total = day_rate × quantity
--
-- The calculated value is stored in service_charges, so future
-- changes to the catalogue price do not change past charges.
-- ============================================================

CREATE OR REPLACE FUNCTION snapshot_service_price()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_day_rate NUMERIC(10,2);
BEGIN

    SELECT day_rate
    INTO v_day_rate
    FROM service_catalogue
    WHERE service_id = NEW.service_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Service % does not exist in the service catalogue',
            NEW.service_id;
    END IF;

    IF NEW.quantity IS NULL OR NEW.quantity <= 0 THEN
        RAISE EXCEPTION
            'Service quantity must be greater than zero';
    END IF;

    IF v_day_rate IS NULL THEN
        RAISE EXCEPTION
            'Service % does not have a valid day rate',
            NEW.service_id;
    END IF;

    NEW.service_total := ROUND(v_day_rate * NEW.quantity, 2);

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_snapshot_service_price
BEFORE INSERT ON service_charges
FOR EACH ROW
EXECUTE FUNCTION snapshot_service_price();