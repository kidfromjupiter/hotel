-- Keep the country code and leading zero available in stored phone numbers.
ALTER TABLE guests
    ALTER COLUMN phone_number TYPE VARCHAR(20)
    USING CASE
        WHEN phone_number IS NULL THEN NULL
        ELSE '+94' || phone_number::TEXT
    END;
