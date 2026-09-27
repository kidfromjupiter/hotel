-- V9: Database functions for guest profiles and membership lookups

-- 1. Get all guests with membership info and search
CREATE OR REPLACE FUNCTION get_all_guests(p_search TEXT DEFAULT NULL)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT COALESCE(
    jsonb_agg(
      jsonb_build_object(
        'guest_id', g.guest_id,
        'name', g.name,
        'national_id', g.national_id,
        'phone_number', g.phone_number::TEXT,
        'membership_id', g.membership_id,
        'membership_name', COALESCE(m.membership_name, 'None'),
        'room_discount_percentage', COALESCE(m.room_discount_percentage, 0.0),
        'service_discount_percentage', COALESCE(m.service_discount_percentage, 0.0)
      )
      ORDER BY g.guest_id ASC
    ),
    '[]'::JSONB
  )
  INTO result
  FROM guests g
  LEFT JOIN skynest_membership m ON g.membership_id = m.membership_id
  WHERE (
    p_search IS NULL
    OR g.name ILIKE ('%' || p_search || '%')
    OR g.national_id ILIKE ('%' || p_search || '%')
    OR g.phone_number::TEXT ILIKE ('%' || p_search || '%')
  );

  RETURN result;
END;
$$;


-- 2. Lookup guest and membership by phone number
CREATE OR REPLACE FUNCTION get_guest_by_phone(p_phone TEXT)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  v_digits TEXT;
  v_phone_int INT;
  result JSONB;
BEGIN
  -- Extract digits from phone string, removing country codes like +94 or leading 0
  v_digits := REGEXP_REPLACE(p_phone, '[^0-9]', '', 'g');
  IF v_digits LIKE '94%' THEN
    v_digits := SUBSTRING(v_digits FROM 3);
  ELSIF v_digits LIKE '0%' THEN
    v_digits := SUBSTRING(v_digits FROM 2);
  END IF;

  BEGIN
    v_phone_int := v_digits::INT;
  EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
  END;

  SELECT jsonb_build_object(
    'guest_id', g.guest_id,
    'name', g.name,
    'national_id', g.national_id,
    'phone_number', g.phone_number::TEXT,
    'membership_id', g.membership_id,
    'has_membership', (g.membership_id IS NOT NULL),
    'membership_name', COALESCE(m.membership_name, 'None'),
    'room_discount_percentage', COALESCE(m.room_discount_percentage, 0.0),
    'service_discount_percentage', COALESCE(m.service_discount_percentage, 0.0)
  )
  INTO result
  FROM guests g
  LEFT JOIN skynest_membership m ON g.membership_id = m.membership_id
  WHERE g.phone_number = v_phone_int
  LIMIT 1;

  RETURN result;
END;
$$;


-- 3. Get single guest by ID
CREATE OR REPLACE FUNCTION get_guest_by_id(p_guest_id INT)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT jsonb_build_object(
    'guest_id', g.guest_id,
    'name', g.name,
    'national_id', g.national_id,
    'phone_number', g.phone_number::TEXT,
    'membership_id', g.membership_id,
    'has_membership', (g.membership_id IS NOT NULL),
    'membership_name', COALESCE(m.membership_name, 'None'),
    'room_discount_percentage', COALESCE(m.room_discount_percentage, 0.0),
    'service_discount_percentage', COALESCE(m.service_discount_percentage, 0.0)
  )
  INTO result
  FROM guests g
  LEFT JOIN skynest_membership m ON g.membership_id = m.membership_id
  WHERE g.guest_id = p_guest_id;

  RETURN result;
END;
$$;


-- 4. Update guest phone number
CREATE OR REPLACE FUNCTION update_guest_phone(p_guest_id INT, p_phone TEXT)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  v_digits TEXT;
  v_phone_int INT;
BEGIN
  v_digits := REGEXP_REPLACE(p_phone, '[^0-9]', '', 'g');
  IF v_digits LIKE '94%' THEN
    v_digits := SUBSTRING(v_digits FROM 3);
  ELSIF v_digits LIKE '0%' THEN
    v_digits := SUBSTRING(v_digits FROM 2);
  END IF;

  BEGIN
    v_phone_int := v_digits::INT;
  EXCEPTION WHEN OTHERS THEN
    RETURN jsonb_build_object('success', false, 'message', 'Invalid phone number format');
  END;

  UPDATE guests
  SET phone_number = v_phone_int
  WHERE guest_id = p_guest_id;

  IF NOT FOUND THEN
    RETURN jsonb_build_object('success', false, 'message', 'Guest not found');
  END IF;

  RETURN jsonb_build_object(
    'success', true,
    'message', 'Phone number updated successfully',
    'guest_id', p_guest_id,
    'phone_number', v_phone_int::TEXT
  );
END;
$$;


-- 5. Enroll guest into membership
CREATE OR REPLACE FUNCTION enroll_guest_membership(p_guest_id INT, p_membership_id INT DEFAULT 1)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE guests
  SET membership_id = p_membership_id
  WHERE guest_id = p_guest_id;

  IF NOT FOUND THEN
    RETURN jsonb_build_object('success', false, 'message', 'Guest not found');
  END IF;

  RETURN jsonb_build_object(
    'success', true,
    'message', 'Guest enrolled in membership successfully',
    'guest_id', p_guest_id,
    'membership_id', p_membership_id
  );
END;
$$;

