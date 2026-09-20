-- ============================================================
-- V7 - Room Status Sync Trigger
-- ============================================================

-- ============================================================
-- Sync room status with booking status.
--
-- Booking Status    Room Status
-- --------------------------------
-- Pending            Reserved
-- Confirmed          Reserved
-- Checked-In        Occupied
-- Checked-Out       Available
-- Cancelled          Available
-- ============================================================

CREATE OR REPLACE FUNCTION sync_room_status_with_booking()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    UPDATE room_details
    SET room_status =
        CASE NEW.booking_status
            WHEN 'Pending' THEN 'Reserved'
            WHEN 'Confirmed' THEN 'Reserved'
            WHEN 'Checked-In' THEN 'Occupied'
            WHEN 'Checked-Out' THEN 'Available'
            WHEN 'Cancelled' THEN 'Available'
        END
    WHERE room_number = NEW.room_number
      AND branch_id = NEW.branch_id;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_sync_room_status
AFTER UPDATE OF booking_status ON booking
FOR EACH ROW
EXECUTE FUNCTION sync_room_status_with_booking();