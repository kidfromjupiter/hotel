CREATE TABLE otp_log (
    otp_id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    otp_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (otp_status IN ('PENDING', 'VERIFIED', 'EXPIRED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
