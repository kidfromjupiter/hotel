from datetime import date
from typing import Any, Dict, List, Optional

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor

class OtpRepository:
    def __init__(self, db: Optional[connection] = None):
        self.db = db
    def save_otp(self, phone: str, otp_code: str, booking_id: Optional[int] = None) -> bool:
        if self.db is not None:
            try:
                with self.db.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO otp_log (phone_number, otp_code, otp_status, created_at, expires_at)
                        VALUES (%s, %s, 'PENDING',NOW(), NOW() + INTERVAL '5 minutes')
                        """,
                        (phone, otp_code),
                    )
                self.db.commit()
                return True
            except Exception:
                self.db.rollback()
                raise
        return False
    
    def verify_otp(self, phone: str, otp: str) -> bool:
        if self.db is not None:
            try:
                with self.db.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT otp_id 
                        FROM otp_log 
                        WHERE phone_number = %s 
                          AND otp_code = %s
                          AND otp_status = 'PENDING'
                          AND expires_at > NOW()
                        ORDER BY otp_id DESC
                        LIMIT 1
                        """,
                        (phone, otp),
                    )
                    row = cursor.fetchone()

                    # If row is None, either the phone or the OTP didn't match (or it expired)
                    if not row:
                        return False
                    #update the otp_status to verified 
                    cursor.execute(
                        "UPDATE otp_log SET otp_status = 'VERIFIED' WHERE otp_id = %s",
                        (row[0],),
                    )
                    self.db.commit()
                    return True

            except Exception:
                self.db.rollback()
                raise
        return False

    def find_phone(self, otp: str) -> Optional[str]: 
        if self.db is not None:
            try:
                with self.db.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT phone_number
                        FROM otp_log 
                        WHERE otp_code = %s
                          AND otp_status = 'VERIFIED'
                        ORDER BY otp_id DESC
                        LIMIT 1
                        """,
                        (otp.strip(),),  # Notice the comma!
                    ) 
                    row = cursor.fetchone()
                    return str(row[0]) if row else None
            except Exception:
                self.db.rollback()
                raise
        return None

                        

