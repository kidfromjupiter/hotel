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
