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
        'description', CASE
          WHEN service_name ILIKE '%Airport%' THEN 'Airport pickup and luxury chauffeur transfer.'
          WHEN service_name ILIKE '%Spa%' THEN 'Full-day access to sauna, steam rooms, and spa.'
          WHEN service_name ILIKE '%Breakfast%' THEN 'Daily gourmet oceanview buffet breakfast.'
          WHEN service_name ILIKE '%Dinner%' THEN 'Lavish evening dining experience.'
          WHEN service_name ILIKE '%Laundry%' THEN 'Professional same-day laundry and pressing service.'
          WHEN service_name ILIKE '%Extra Bed%' THEN 'Additional rollaway bed with premium linens.'
          ELSE service_name
        END,
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
