from datetime import date


def test_overlapping_booking_excludes_room(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO branches (branch_id, branch_name)
            VALUES (9001, 'test-kandy');

            INSERT INTO room_types (room_type_id, daily_rate)
            VALUES ('TEST_STANDARD', 15000);

            INSERT INTO skynest_membership
                (membership_id, membership_name,
                 room_discount_percentage, service_discount_percentage)
            VALUES (9001, 'Test', 0, 0);

            INSERT INTO guests
                (guest_id, membership_id, name, national_id, phone_number)
            VALUES (9001, 9001, 'Test Guest', 'TEST9001', 771111111);

            INSERT INTO room_details
                (room_number, branch_id, room_type_id, room_status, capacity)
            VALUES
                (101, 9001, 'TEST_STANDARD', 'AVAILABLE', 2),
                (102, 9001, 'TEST_STANDARD', 'AVAILABLE', 2);

            INSERT INTO booking
                (booking_id, room_number, branch_id, guest_id,
                 booking_status, start_date, end_date,
                 adult_count, children_count)
            VALUES
                (9001, 102, 9001, 9001,
                 'CONFIRMED', '2026-10-01', '2026-10-03', 2, 0);
        """)

        cursor.execute(
            "SELECT get_available_rooms(%s, %s, %s, %s, %s)",
            (date(2026, 10, 2), date(2026, 10, 4), "test-kandy", 0, 2),
        )
        rooms = cursor.fetchone()[0]

    assert {(room["branch_id"], room["room_number"]) for room in rooms} == {(9001, 101)}
