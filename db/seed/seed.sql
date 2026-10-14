-- =====================================================================
-- HRGSMS / SkyNest
-- SEED DATA
-- PostgreSQL
--
-- IMPORTANT:
-- Run ALL migration files first.
-- This seed file assumes:
--   1. All tables have been created
--   2. transactions table has been created
--   3. transactions.payment_method has been added
--   4. transactions.invoice_id has its FK to billing_summary(invoice_id)
-- =====================================================================

SET TIME ZONE 'Asia/Colombo';


-- =====================================================================
-- 1. SKYNEST MEMBERSHIP
-- =====================================================================

INSERT INTO skynest_membership (
    membership_id,
    membership_name,
    room_discount_percentage,
    service_discount_percentage
)
VALUES
    (1, 'Basic',     5.00,  5.00),
    (2, 'Silver',   10.00, 10.00),
    (3, 'Gold',     15.00, 15.00),
    (4, 'Platinum', 20.00, 20.00);


-- =====================================================================
-- 2. TAX POLICIES
-- =====================================================================

INSERT INTO tax_policies (
    tax_id,
    tax_name,
    active,
    tax_percentage
)
VALUES
    (1, 'VAT',         TRUE,  15.00),
    (2, 'Service Tax', FALSE,  5.00),
    (3, 'Tourism Tax', FALSE,  2.00);


-- =====================================================================
-- 3. BRANCHES
-- =====================================================================

INSERT INTO branches (
    branch_id,
    branch_name
)
VALUES
    (1, 'colombo'),
    (2, 'kandy'),
    (3, 'galle');


-- =====================================================================
-- 4. ROOM TYPES
-- =====================================================================

INSERT INTO room_types (
    room_type_id,
    daily_rate
)
VALUES
    ('STANDARD', 15000.00),
    ('DELUXE',   22000.00),
    ('SUITE',    35000.00),
    ('FAMILY',   28000.00);

UPDATE room_types SET capacity = CASE WHEN room_type_id = 'FAMILY' THEN 4 ELSE 2 END;


-- =====================================================================
-- 5. AMENITIES
-- =====================================================================
-- these amenities are what's included with the room.
INSERT INTO amenities (
    amenity_id,
    amenity_name
)
VALUES
    (1, 'WiFi'),
    (2, 'Air Conditioning'),
    (3, 'Mini Bar'),
    (4, 'Television'),
    (5, 'Swimming Pool Access'),
    (6, 'King Size Bed'),
    (7, 'Room Safe'),
    (8, 'Hair Dryer');


-- =====================================================================
-- 6. SERVICE CATALOGUE
-- =====================================================================

INSERT INTO service_catalogue (
    service_id,
    service_name,
    day_rate
)
VALUES
    (1, 'Airport Transfer', 5000.00),
    (2, 'Laundry',          1500.00),
    (3, 'Room Service',     2500.00),
    (4, 'Spa',              7500.00),
    (5, 'Breakfast',        3000.00),
    (6, 'Dinner',           4500.00),
    (7, 'Extra Bed',        4000.00);


-- =====================================================================
-- 7. GUESTS
-- =====================================================================

INSERT INTO guests (
    guest_id,
    membership_id,
    name,
    national_id,
    phone_number
)
VALUES
    (1, 1, 'Amal Perera',      '199812345678', '+94771234567'),
    (2, 2, 'Nimal Fernando',   '199923456789', '+94772345678'),
    (3, 3, 'Kavindi Silva',    '200045678901', '+94773456789'),
    (4, 4, 'Sahan Jayasinghe', '199756789012', '+94774567890'),
    (5, 1, 'Tharushi Perera',  '200112345678', '+94775678901');


-- =====================================================================
-- 8. ROOM DETAILS
-- =====================================================================

INSERT INTO room_details (
    room_number,
    branch_id,
    room_type_id,
    room_status,
    capacity
)
VALUES
    -- Colombo Branch
    (101, 1, 'STANDARD', 'AVAILABLE',2),
    (102, 1, 'STANDARD', 'OCCUPIED',2),
    (103, 1, 'STANDARD', 'OCCUPIED',2),
    (201, 1, 'DELUXE',   'OCCUPIED',2),
    (202, 1, 'DELUXE',   'AVAILABLE',2),
    (301, 1, 'SUITE',    'MAINTENANCE',2),
    (401, 1, 'FAMILY',   'AVAILABLE',4),

    -- Kandy Branch
    (101, 2, 'STANDARD', 'AVAILABLE',2),
    (102, 2, 'DELUXE',   'AVAILABLE',2),
    (201, 2, 'SUITE',    'AVAILABLE',2),
    (301, 2, 'FAMILY',   'AVAILABLE',4),

    -- Galle Branch
    (101, 3, 'STANDARD', 'AVAILABLE',2),
    (102, 3, 'DELUXE',   'AVAILABLE',2),
    (201, 3, 'SUITE',    'AVAILABLE',2),
    (301, 3, 'FAMILY',   'OCCUPIED',4);


-- =====================================================================
-- 9. ROOM AMENITIES
-- =====================================================================

INSERT INTO room_amenities (
    amenity_id,
    room_type_id
)
VALUES
    -- STANDARD
    (1, 'STANDARD'),
    (2, 'STANDARD'),
    (4, 'STANDARD'),
    (7, 'STANDARD'),
    (8, 'STANDARD'),

    -- DELUXE
    (1, 'DELUXE'),
    (2, 'DELUXE'),
    (3, 'DELUXE'),
    (4, 'DELUXE'),
    (6, 'DELUXE'),
    (7, 'DELUXE'),
    (8, 'DELUXE'),

    -- SUITE
    (1, 'SUITE'),
    (2, 'SUITE'),
    (3, 'SUITE'),
    (4, 'SUITE'),
    (5, 'SUITE'),
    (6, 'SUITE'),
    (7, 'SUITE'),
    (8, 'SUITE'),

    -- FAMILY
    (1, 'FAMILY'),
    (2, 'FAMILY'),
    (4, 'FAMILY'),
    (5, 'FAMILY'),
    (6, 'FAMILY'),
    (7, 'FAMILY'),
    (8, 'FAMILY');


-- =====================================================================
-- 10. BOOKINGS
-- =====================================================================

INSERT INTO booking (
    booking_id,
    booking_ref,
    room_number,
    branch_id,
    guest_id,
    booking_status,
    start_date,
    end_date,
    checked_in_time,
    checked_out_time,
    adult_count,
    children_count,
    nightly_rate,
    room_discount_percentage
)
VALUES

    -- Booking 1001 - Checked in and paid
    (
        1001,
        'SKN-1001',
        102,
        1,
        1,
        'CHECKED_IN',
        CURRENT_DATE - 1,
        CURRENT_DATE + 3,
        '14:00:00',
        NULL,
        2,
        0,
        15000.00,
        5.00
    ),

    -- Booking 1002 - Checked in with a partial payment
    (
        1002,
        'SKN-1002',
        201,
        1,
        2,
        'CHECKED_IN',
        CURRENT_DATE - 1,
        CURRENT_DATE + 2,
        '14:00:00',
        NULL,
        2,
        0,
        22000.00,
        10.00
    ),

    -- Booking 1003 - Completed
    (
        1003,
        'SKN-1003',
        201,
        2,
        3,
        'CHECKED_OUT',
        CURRENT_DATE - 30,
        CURRENT_DATE - 27,
        '13:30:00',
        '11:00:00',
        2,
        0,
        35000.00,
        15.00
    ),

    -- Booking 1004 - Completed
    (
        1004,
        'SKN-1004',
        201,
        3,
        4,
        'CHECKED_OUT',
        CURRENT_DATE - 25,
        CURRENT_DATE - 22,
        '14:00:00',
        '10:30:00',
        2,
        0,
        35000.00,
        20.00
    ),

    -- Booking 1005 - Checked in with a partial payment
    (
        1005,
        'SKN-1005',
        103,
        1,
        5,
        'CHECKED_IN',
        CURRENT_DATE - 1,
        CURRENT_DATE + 2,
        '14:00:00',
        NULL,
        1,
        0,
        15000.00,
        5.00
    ),

    -- Booking 1006 - Cancelled
    (
        1006,
        'SKN-1006',
        301,
        2,
        1,
        'CANCELLED',
        CURRENT_DATE + 5,
        CURRENT_DATE + 7,
        NULL,
        NULL,
        2,
        0,
        28000.00,
        5.00
    ),

    -- Booking 1007 - Checked in with a partial payment
    (
        1007,
        'SKN-1007',
        301,
        3,
        2,
        'CHECKED_IN',
        CURRENT_DATE - 1,
        CURRENT_DATE + 3,
        '14:00:00',
        NULL,
        2,
        2,
        28000.00,
        10.00
    ),

    -- Booking 1008 - Future booking
    (
        1008,
        'SKN-1008',
        101,
        2,
        3,
        'CONFIRMED',
        CURRENT_DATE + 10,
        CURRENT_DATE + 12,
        NULL,
        NULL,
        1,
        0,
        15000.00,
        15.00
    );


-- =====================================================================
-- 11. BILLING SUMMARY
-- =====================================================================

INSERT INTO billing_summary (
    invoice_id,
    payment_method,
    booking_id,
    total_room_charges,
    total_service_charges,
    total_tax_amount,
    grand_total,
    amount_paid,
    payment_status
)
VALUES

    -- Invoice for Booking 1001
    (
        '11111111-1111-1111-1111-111111111111',
        'CARD',
        1001,
        57000.00,
        7600.00,
        9690.00,
        74290.00,
        74290.00,
        'PAID'
    ),

    -- Invoice for Booking 1002
    (
        '22222222-2222-2222-2222-222222222222',
        'CASH',
        1002,
        59400.00,
        2700.00,
        9315.00,
        71415.00,
        40000.00,
        'PARTIALLY_PAID'
    ),

    -- Invoice for Booking 1003
    (
        '33333333-3333-3333-3333-333333333333',
        'CARD',
        1003,
        89250.00,
        6375.00,
        14343.75,
        109968.75,
        109968.75,
        'PAID'
    ),

    -- Invoice for Booking 1004
    (
        '44444444-4444-4444-4444-444444444444',
        'CARD',
        1004,
        84000.00,
        7200.00,
        13680.00,
        104880.00,
        104880.00,
        'PAID'
    ),

    -- Invoice for Booking 1005
    (
        '55555555-5555-5555-5555-555555555555',
        'CASH',
        1005,
        42750.00,
        0.00,
        6412.50,
        49162.50,
        20000.00,
        'PARTIALLY_PAID'
    ),

    -- Invoice for Booking 1007
    (
        '66666666-6666-6666-6666-666666666666',
        'CARD',
        1007,
        100800.00,
        0.00,
        15120.00,
        115920.00,
        10000.00,
        'PARTIALLY_PAID'
    ),

    -- Invoice for Booking 1008
    (
        '77777777-7777-7777-7777-777777777777',
        'CARD',
        1008,
        25500.00,
        0.00,
        3825.00,
        29325.00,
        0.00,
        'UNPAID'
    );


-- =====================================================================
-- 12. SERVICE CHARGES
-- =====================================================================

INSERT INTO service_charges (
    service_log_id,
    booking_id,
    service_id,
    quantity,
    usage_date,
    unit_price,
    discount_percentage,
    service_total
)
VALUES
    (1, 1001, 1, 1, CURRENT_DATE, 5000.00, 5.00, 4750.00),
    (2, 1001, 5, 1, CURRENT_DATE, 3000.00, 5.00, 2850.00),
    (3, 1002, 5, 1, CURRENT_DATE, 3000.00, 10.00, 2700.00),
    (4, 1003, 4, 1, CURRENT_DATE - 28, 7500.00, 15.00, 6375.00),
    (5, 1004, 1, 1, CURRENT_DATE - 24, 5000.00, 20.00, 4000.00),
    (6, 1004, 7, 1, CURRENT_DATE - 24, 4000.00, 20.00, 3200.00);


-- =====================================================================
-- 13. INVOICE TAXES
-- =====================================================================

INSERT INTO invoice_taxes (
    invoice_id,
    tax_id,
    calculated_amount
)
VALUES

    -- Invoice 1111
    (
        '11111111-1111-1111-1111-111111111111',
        1,
        9690.00
    ),

    -- Invoice 2222
    (
        '22222222-2222-2222-2222-222222222222',
        1,
        9315.00
    ),

    -- Invoice 3333
    (
        '33333333-3333-3333-3333-333333333333',
        1,
        14343.75
    ),

    -- Invoice 4444
    (
        '44444444-4444-4444-4444-444444444444',
        1,
        13680.00
    ),

    -- Invoice 5555
    (
        '55555555-5555-5555-5555-555555555555',
        1,
        6412.50
    ),

    -- Invoice 6666
    (
        '66666666-6666-6666-6666-666666666666',
        1,
        15120.00
    ),
    (
        '77777777-7777-7777-7777-777777777777',
        1,
        3825.00
    );


-- =====================================================================
-- 15. TRANSACTIONS
-- =====================================================================
--
-- transactions table:
--
-- transaction_id UUID PRIMARY KEY
-- invoice_id UUID
-- payment_date TIMESTAMP
-- amount NUMERIC(10,2)
--
-- payment_method is added by another migration.
-- =====================================================================

INSERT INTO transactions (
    transaction_id,
    invoice_id,
    payment_date,
    amount,
    payment_method,
    room_amount,
    service_amount,
    tax_amount
)
VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', CURRENT_TIMESTAMP, 74290.00, 'CARD', 57000.00, 7600.00, 9690.00),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '22222222-2222-2222-2222-222222222222', CURRENT_TIMESTAMP, 40000.00, 'CASH', 33270.32, 1512.29, 5217.39),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', '33333333-3333-3333-3333-333333333333', CURRENT_TIMESTAMP - INTERVAL '27 days', 109968.75, 'CARD', 89250.00, 6375.00, 14343.75),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', '44444444-4444-4444-4444-444444444444', CURRENT_TIMESTAMP - INTERVAL '24 days', 60000.00, 'CARD', 48054.92, 4118.99, 7826.09),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '44444444-4444-4444-4444-444444444444', CURRENT_TIMESTAMP - INTERVAL '22 days', 44880.00, 'CARD', 35945.08, 3081.01, 5853.91),
    ('ffffffff-ffff-ffff-ffff-ffffffffffff', '55555555-5555-5555-5555-555555555555', CURRENT_TIMESTAMP, 20000.00, 'CARD', 17391.30, 0.00, 2608.70),
    ('99999999-9999-9999-9999-999999999999', '66666666-6666-6666-6666-666666666666', CURRENT_TIMESTAMP, 10000.00, 'CARD', 8695.65, 0.00, 1304.35);

-- =====================================================================
-- 16. STAFF (AUTHENTICATION)
-- =====================================================================

INSERT INTO staff (
    staff_id,
    branch_id,
    username,
    password_hash,
    full_name,
    role,
    is_active
)
VALUES
    -- Admin: access to all branches (branch_id is NULL)
    -- Default password: "adminPassword123" (bcrypt hash)
    (
        1,
        NULL,
        'admin',
        '$2b$12$99HpfqysYSTxXsEJqQR34u/xcv05X/XRccDLIlYw.ggsc9OamywRC',
        'System Administrator',
        'admin',
        TRUE
    ),
    -- Receptionist for Colombo (branch_id = 1)
    -- Default password: "colomboPassword123" (bcrypt hash)
    (
        2,
        1,
        'rec_colombo',
        '$2b$12$9VyZStpePH4IKS3TjE0zWOYA164OIfRjV/.eFgU4bMlyYwF0p4tji',
        'Colombo Reception Desk',
        'receptionist',
        TRUE
    ),
    -- Receptionist for Kandy (branch_id = 2)
    -- Default password: "kandyPassword123" (bcrypt hash)
    (
        3,
        2,
        'rec_kandy',
        '$2b$12$TpjfB3BlablrrO3r3LBzgurkSQdG.NfXBVmJ.7jHT0iI4RXc7lMpS',
        'Kandy Reception Desk',
        'receptionist',
        TRUE
    ),
    -- Receptionist for Galle (branch_id = 3)
    -- Default password: "gallePassword123" (bcrypt hash)
    (
        4,
        3,
        'rec_galle',
        '$2b$12$pjzsYcJhuKTOMRLNp3pDV.EuzecRzyuQx43A1OdGYNpp2ILsFT/5O',
        'Galle Reception Desk',
        'receptionist',
        TRUE
    );



-- =====================================================================
-- END OF SEED DATA
-- =====================================================================


-- Synchronize identity sequences after inserting explicit seed IDs.
-- Run seeding before starting application traffic.
BEGIN;
LOCK TABLE booking, guests, service_charges, staff IN ACCESS EXCLUSIVE MODE;

DO $$
DECLARE
    item RECORD;
    sequence_name TEXT;
    highest_id BIGINT;
    sequence_value BIGINT;
BEGIN
    FOR item IN
        SELECT *
        FROM (VALUES
            ('booking', 'booking_id'),
            ('guests', 'guest_id'),
            ('service_charges', 'service_log_id'),
            ('staff', 'staff_id')
        ) AS ids(table_name, column_name)
    LOOP
        sequence_name := pg_get_serial_sequence(
            item.table_name, item.column_name
        );

        EXECUTE format(
            'SELECT COALESCE(MAX(%I), 0) FROM %I',
            item.column_name, item.table_name
        ) INTO highest_id;

        EXECUTE format(
            'SELECT last_value FROM %s', sequence_name
        ) INTO sequence_value;

        PERFORM setval(
            sequence_name::regclass,
            GREATEST(highest_id, sequence_value, 1),
            true
        );
    END LOOP;
END;
$$;
COMMIT;
