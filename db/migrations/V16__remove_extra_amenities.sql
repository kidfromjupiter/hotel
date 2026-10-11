-- Extra amenities were an incomplete duplicate of the service catalogue.
-- Existing extra-amenity records are intentionally removed rather than migrated.

DROP FUNCTION IF EXISTS add_extra_amenity_to_booking(BIGINT, INT, INT);
DROP FUNCTION IF EXISTS get_branch_amenities(TEXT);

DROP TABLE IF EXISTS booking_extra_amenities;
DROP TABLE IF EXISTS extra_amenities;
