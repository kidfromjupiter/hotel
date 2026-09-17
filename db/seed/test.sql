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
    (2, 'Service Tax', TRUE,   5.00),
    (3, 'Tourism Tax', FALSE,  2.00);


-- =====================================================================
-- 3. BRANCHES
-- =====================================================================

INSERT INTO branches (
    branch_id,
    branch_name
)
VALUES
    (1, 'Colombo'),
    (2, 'Kandy'),
    (3, 'Galle');


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


-- =====================================================================
-- 5. AMENITIES
-- =====================================================================

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
    (1, 1, 'Amal Perera',      '199812345678', 771234567),
    (2, 2, 'Nimal Fernando',   '199923456789', 772345678),
    (3, 3, 'Kavindi Silva',    '200045678901', 773456789),
    (4, 4, 'Sahan Jayasinghe', '199756789012', 774567890),
    (5, 1, 'Tharushi Perera',  '200112345678', 775678901),
    (6, 2, 'Dilan Wijesinghe', '199634567890', 776789012),
    (7, 3, 'Hiruni Fernando',  '200234567890', 777890123),
    (8, 1, 'Kasun Bandara',    '199845678901', 778901234);


-- =====================================================================
-- 8. ROOM DETAILS
-- =====================================================================

INSERT INTO room_details (
    room_number,
    branch_id,
    room_type_id,
    room_status
)
VALUES
    -- Colombo Branch
    (101, 1, 'STANDARD', 'AVAILABLE'),
    (102, 1, 'STANDARD', 'OCCUPIED'),
    (103, 1, 'STANDARD', 'AVAILABLE'),
    (201, 1, 'DELUXE',   'AVAILABLE'),
    (202, 1, 'DELUXE',   'AVAILABLE'),
    (301, 1, 'SUITE',    'MAINTENANCE'),
    (401, 1, 'FAMILY',   'AVAILABLE'),

    -- Kandy Branch
    (101, 2, 'STANDARD', 'AVAILABLE'),
    (102, 2, 'DELUXE',   'OCCUPIED'),
    (201, 2, 'SUITE',    'AVAILABLE'),
    (301, 2, 'FAMILY',   'AVAILABLE'),

    -- Galle Branch
    (101, 3, 'STANDARD', 'AVAILABLE'),
    (102, 3, 'DELUXE',   'AVAILABLE'),
    (201, 3, 'SUITE',    'OCCUPIED'),
    (301, 3, 'FAMILY',   'AVAILABLE');


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
    room_number,
    branch_id,
    guest_id,
    booking_status,
    start_date,
    end_date,
    checked_in_time,
    checked_out_time,
    adult_count,
    children_count
)
VALUES

    -- Booking 1001 - Currently checked in
    (
        1001,
        102,
        1,
        1,
        'CHECKED_IN',
        '2026-09-01',
        '2026-09-05',
        '14:00:00',
        NULL,
        2,
        0
    ),

    -- Booking 1002 - Future booking
    (
        1002,
        201,
        1,
        2,
        'CONFIRMED',
        '2026-09-10',
        '2026-09-13',
        NULL,
        NULL,
        2,
        1
    ),

    -- Booking 1003 - Completed
    (
        1003,
        201,
        2,
        3,
        'COMPLETED',
        '2026-08-20',
        '2026-08-23',
        '13:30:00',
        '11:00:00',
        2,
        0
    ),

    -- Booking 1004 - Completed
    (
        1004,
        201,
        3,
        4,
        'COMPLETED',
        '2026-08-25',
        '2026-08-28',
        '14:00:00',
        '10:30:00',
        2,
        2
    ),

    -- Booking 1005 - Future booking
    (
        1005,
        103,
        1,
        5,
        'CONFIRMED',
        '2026-09-15',
        '2026-09-18',
        NULL,
        NULL,
        1,
        0
    ),

    -- Booking 1006 - Cancelled
    (
        1006,
        301,
        2,
        6,
        'CANCELLED',
        '2026-09-05',
        '2026-09-07',
        NULL,
        NULL,
        2,
        0
    ),

    -- Booking 1007 - Future family booking
    (
        1007,
        301,
        3,
        7,
        'CONFIRMED',
        '2026-09-20',
        '2026-09-24',
        NULL,
        NULL,
        2,
        2
    ),

    -- Booking 1008 - Completed
    (
        1008,
        101,
        2,
        8,
        'COMPLETED',
        '2026-08-15',
        '2026-08-17',
        '14:30:00',
        '11:00:00',
        1,
        0
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
        60000.00,
        8000.00,
        10200.00,
        78200.00,
        78200.00,
        'PAID'
    ),

    -- Invoice for Booking 1002
    (
        '22222222-2222-2222-2222-222222222222',
        'CASH',
        1002,
        66000.00,
        3000.00,
        10350.00,
        79350.00,
        40000.00,
        'PARTIALLY_PAID'
    ),

    -- Invoice for Booking 1003
    (
        '33333333-3333-3333-3333-333333333333',
        'CARD',
        1003,
        44000.00,
        7500.00,
        7725.00,
        59225.00,
        59225.00,
        'PAID'
    ),

    -- Invoice for Booking 1004
    (
        '44444444-4444-4444-4444-444444444444',
        'CARD',
        1004,
        84000.00,
        9000.00,
        13950.00,
        106950.00,
        106950.00,
        'PAID'
    ),

    -- Invoice for Booking 1005
    (
        '55555555-5555-5555-5555-555555555555',
        'CASH',
        1005,
        45000.00,
        0.00,
        6750.00,
        51750.00,
        0.00,
        'PENDING'
    ),

    -- Invoice for Booking 1008
    (
        '66666666-6666-6666-6666-666666666666',
        'CARD',
        1008,
        30000.00,
        3000.00,
        4950.00,
        37950.00,
        37950.00,
        'PAID'
    );


-- =====================================================================
-- 12. SERVICE CHARGES
-- =====================================================================

INSERT INTO service_charges (
    service_log_id,
    booking_id,
    service_id,
    service_dates,
    service_total
)
VALUES
    (1, 1001, 1, 1, 5000.00),
    (2, 1001, 5, 1, 3000.00),

    (3, 1002, 5, 1, 3000.00),

    (4, 1003, 4, 1, 7500.00),

    (5, 1004, 1, 1, 5000.00),
    (6, 1004, 7, 1, 4000.00),

    (7, 1008, 2, 2, 3000.00);


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
        10200.00
    ),

    -- Invoice 2222
    (
        '22222222-2222-2222-2222-222222222222',
        1,
        10350.00
    ),

    -- Invoice 3333
    (
        '33333333-3333-3333-3333-333333333333',
        1,
        7725.00
    ),

    -- Invoice 4444
    (
        '44444444-4444-4444-4444-444444444444',
        1,
        13950.00
    ),

    -- Invoice 5555
    (
        '55555555-5555-5555-5555-555555555555',
        1,
        6750.00
    ),

    -- Invoice 6666
    (
        '66666666-6666-6666-6666-666666666666',
        1,
        4950.00
    );


-- =====================================================================
-- 14. BOOKING EXTRA AMENITIES
-- =====================================================================

INSERT INTO booking_extra_amenities (
    booking_id,
    amenity_id,
    quantity
)
VALUES
    (1001, 3, 1),
    (1001, 5, 2),

    (1002, 5, 3),

    (1003, 3, 1),

    (1004, 5, 4),

    (1005, 3, 1),

    (1007, 5, 4),

    (1008, 3, 1);


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
    payment_method
)
VALUES

    -- Invoice 1111 / Booking 1001
    -- Fully paid: 78,200
    (
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        '11111111-1111-1111-1111-111111111111',
        '2026-09-01 14:15:00',
        78200.00,
        'CARD'
    ),

    -- Invoice 2222 / Booking 1002
    -- Partially paid: 40,000
    (
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        '22222222-2222-2222-2222-222222222222',
        '2026-09-02 10:30:00',
        40000.00,
        'CASH'
    ),

    -- Invoice 3333 / Booking 1003
    -- Fully paid: 59,225
    (
        'cccccccc-cccc-cccc-cccc-cccccccccccc',
        '33333333-3333-3333-3333-333333333333',
        '2026-08-23 11:30:00',
        59225.00,
        'CARD'
    ),

    -- Invoice 4444 / Booking 1004
    -- Fully paid using two transactions
    -- 60,000 + 46,950 = 106,950
    (
        'dddddddd-dddd-dddd-dddd-dddddddddddd',
        '44444444-4444-4444-4444-444444444444',
        '2026-08-25 13:00:00',
        60000.00,
        'CARD'
    ),

    (
        'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
        '44444444-4444-4444-4444-444444444444',
        '2026-08-28 10:45:00',
        46950.00,
        'CARD'
    ),

    -- Invoice 6666 / Booking 1008
    -- Fully paid: 37,950
    (
        'ffffffff-ffff-ffff-ffff-ffffffffffff',
        '66666666-6666-6666-6666-666666666666',
        '2026-08-17 11:15:00',
        37950.00,
        'CARD'
    );


-- =====================================================================
-- END OF SEED DATA
-- =====================================================================