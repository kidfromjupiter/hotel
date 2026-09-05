-- 1. Independent Tables
CREATE TABLE skynest_membership (
    membership_id INT PRIMARY KEY,
    membership_name VARCHAR(255),
    room_discount_percentage DECIMAL(10,2),
    service_discount_percentage DECIMAL(10,2)
);

CREATE TABLE tax_policies (
    tax_id INT PRIMARY KEY,
    tax_name VARCHAR(20),
    active BOOLEAN,
    tax_percentage DECIMAL(10,2)
);

CREATE TABLE branches (
    branch_id INT PRIMARY KEY,
    branch_name VARCHAR(255)
);

CREATE TABLE room_types (
    room_type_id VARCHAR(50) PRIMARY KEY,
    daily_rate DECIMAL(10,2)
);

CREATE TABLE amenities (
    amentity_id INT PRIMARY KEY,
    amentity_name VARCHAR(255)
);

CREATE TABLE service_catalogue (
    service_id INT PRIMARY KEY,
    service_name VARCHAR(255),
    day_rate DECIMAL(10,2)
);

-- 2. First-level Dependent Tables
CREATE TABLE guests (
    guest_id INT PRIMARY KEY,
    membership_id INT,
    name VARCHAR(255),
    national_id VARCHAR(20),
    phone_number INT,
    FOREIGN KEY (membership_id)
        REFERENCES skynest_membership(membership_id)
);

CREATE TABLE room_details (
    room_number SMALLINT,
    branch_id INT,
    room_type_id VARCHAR(50),
    room_status VARCHAR(50),
    PRIMARY KEY (room_number, branch_id),
    FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id),
    FOREIGN KEY (room_type_id)
        REFERENCES room_types(room_type_id)
);

CREATE TABLE room_amenities (
    amenity_id INT,
    room_type_id VARCHAR(50),
    PRIMARY KEY (amenity_id, room_type_id),
    FOREIGN KEY (amenity_id)
        REFERENCES amenities(amenity_id),
    FOREIGN KEY (room_type_id)
        REFERENCES room_types(room_type_id)
);

-- 3. Bookings and onward
CREATE TABLE booking (
    booking_id BIGINT PRIMARY KEY,
    room_number SMALLINT,
    branch_id INT,
    guest_id INT,
    booking_status VARCHAR(50),
    start_date DATE,
    end_date DATE,
    checked_in_time TIME,
    checked_out_time TIME,
    adult_count INT,
    children_count INT,
    FOREIGN KEY (room_number, branch_id)
        REFERENCES room_details(room_number, branch_id),
    FOREIGN KEY (guest_id)
        REFERENCES guests(guest_id)
);

CREATE TABLE billing_summary (
    invoice_id UUID PRIMARY KEY,
    payment_method VARCHAR(50),
    booking_id BIGINT,
    total_room_charges DECIMAL(10,2),
    total_service_charges DECIMAL(10,2),
    total_tax_amount DECIMAL(10,2),
    grand_total DECIMAL(10,2),
    amount_paid DECIMAL(10,2),
    payment_status VARCHAR(50),
    FOREIGN KEY (booking_id)
        REFERENCES booking(booking_id)
);

CREATE TABLE service_charges (
    service_log_id INT PRIMARY KEY,
    booking_id BIGINT,
    service_id INT,
    service_dates INT,
    service_total DECIMAL(10,2),
    FOREIGN KEY (booking_id)
        REFERENCES booking(booking_id),
    FOREIGN KEY (service_id)
        REFERENCES service_catalogue(service_id)
);

CREATE TABLE invoice_taxes (
    invoice_id UUID,
    tax_id INT,
    calculated_amount DECIMAL(10,2),
    PRIMARY KEY (invoice_id, tax_id),
    FOREIGN KEY (invoice_id)
        REFERENCES billing_summary(invoice_id),
    FOREIGN KEY (tax_id)
        REFERENCES tax_policies(tax_id)
);

CREATE TABLE booking_extra_amenities (
    booking_id BIGINT,
    amentity_id INT,
    quantity INT,
    PRIMARY KEY (booking_id, amentity_id),
    FOREIGN KEY (booking_id)
        REFERENCES booking(booking_id),
    FOREIGN KEY (amentity_id)
        REFERENCES amenities(amentity_id)
);

ALTER TABLE transactions
ADD COLUMN payment_method VARCHAR(50),
ADD CONSTRAINT fk_invoice
    FOREIGN KEY (invoice_id)
    REFERENCES billing_summary(invoice_id);
