-- Add description column to service_catalogue table if it doesn't exist
ALTER TABLE service_catalogue
ADD COLUMN IF NOT EXISTS description TEXT;

-- Populate default descriptions
UPDATE service_catalogue SET description = 'Airport pickup and luxury chauffeur transfer.' WHERE service_name ILIKE '%Airport%' AND (description IS NULL OR description = '');
UPDATE service_catalogue SET description = 'Full-day access to sauna, steam rooms, and spa.' WHERE service_name ILIKE '%Spa%' AND (description IS NULL OR description = '');
UPDATE service_catalogue SET description = 'Daily gourmet oceanview buffet breakfast.' WHERE service_name ILIKE '%Breakfast%' AND (description IS NULL OR description = '');
UPDATE service_catalogue SET description = 'Lavish evening dining experience.' WHERE service_name ILIKE '%Dinner%' AND (description IS NULL OR description = '');
UPDATE service_catalogue SET description = 'Professional same-day laundry and pressing service.' WHERE service_name ILIKE '%Laundry%' AND (description IS NULL OR description = '');
UPDATE service_catalogue SET description = 'Additional rollaway bed with premium linens.' WHERE service_name ILIKE '%Extra Bed%' AND (description IS NULL OR description = '');
UPDATE service_catalogue SET description = service_name WHERE description IS NULL;

-- Functions for fetching branches and amenities / add-on services

CREATE OR REPLACE FUNCTION get_all_branches()
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT COALESCE(
    jsonb_agg(
      jsonb_build_object(
        'branch_id', branch_id,
        'branch_name', INITCAP(branch_name)
      )
      ORDER BY branch_id
    ),
    '[]'::JSONB
  )
  INTO result
  FROM branches;

  RETURN result;
END;
$$;


CREATE OR REPLACE FUNCTION get_branch_amenities(p_branch TEXT)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT COALESCE(
    jsonb_agg(
      jsonb_build_object(
        'id', LOWER(REPLACE(service_name, ' ', '-')),
        'service_id', service_id,
        'name', service_name,
        'price', day_rate,
        'description', COALESCE(description, service_name),
        'icon', CASE
          WHEN service_name ILIKE '%Airport%' THEN 'car'
          WHEN service_name ILIKE '%Spa%' THEN 'spa'
          WHEN service_name ILIKE '%Breakfast%' THEN 'restaurant'
          WHEN service_name ILIKE '%Dinner%' THEN 'restaurant'
          WHEN service_name ILIKE '%Laundry%' THEN 'waves'
          ELSE 'star'
        END
      )
      ORDER BY service_id
    ),
    '[]'::JSONB
  )
  INTO result
  FROM service_catalogue;

  RETURN result;
END;
$$;

