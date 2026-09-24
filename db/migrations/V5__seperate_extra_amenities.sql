-- Existing extra-amenity rows keep their IDs and quantities.
-- No historic prices exist, so existing prices start at 0 and need review.

CREATE TABLE extra_amenities (
    extra_amenity_id INT PRIMARY KEY,
    extra_amenity_name VARCHAR(255) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (unit_price >= 0)
);

INSERT INTO extra_amenities (extra_amenity_id, extra_amenity_name, unit_price)
SELECT DISTINCT a.amenity_id, a.amenity_name, 0
FROM amenities AS a
JOIN booking_extra_amenities AS bea ON bea.amenity_id = a.amenity_id;

ALTER TABLE booking_extra_amenities
    DROP CONSTRAINT booking_extra_amenities_amenity_id_fkey;

ALTER TABLE booking_extra_amenities
    RENAME COLUMN amenity_id TO extra_amenity_id;

ALTER TABLE booking_extra_amenities
    ADD COLUMN unit_price NUMERIC(10, 2) NOT NULL DEFAULT 0,
    ADD CONSTRAINT booking_extra_amenities_price_nonnegative CHECK (unit_price >= 0),
    ADD CONSTRAINT booking_extra_amenities_quantity_positive CHECK (quantity > 0),
    ADD CONSTRAINT booking_extra_amenities_extra_amenity_id_fkey
        FOREIGN KEY (extra_amenity_id) REFERENCES extra_amenities(extra_amenity_id);
