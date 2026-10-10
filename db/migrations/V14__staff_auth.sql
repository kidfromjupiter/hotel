CREATE TABLE IF NOT EXISTS staff (
    staff_id SERIAL PRIMARY KEY,
    branch_id INT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'receptionist')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id)
);

CREATE INDEX IF NOT EXISTS idx_staff_username ON staff (username);
