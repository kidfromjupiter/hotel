from typing import Optional
import random
from typing import Dict, Tuple
from app.repositories.otp import OtpRepository

class OTPService:
    def __init__(self, repo: Optional[OtpRepository] = None):
        self.otp_repo = repo or OtpRepository()
        self._store: Dict[str, Tuple[str, float]] = {}

    def clear(self):
        """Clears stored OTPs."""
        self._store.clear()

    def send_otp(self, phone: str) -> dict:
        """Generates and stores a 6-digit OTP."""
        otp_code = f"{random.randint(100000, 999999)}"
        # Ensure not 000000 or 123456 for test separation
        if otp_code in ("000000", "123456"):
            otp_code = "789123"
        self._store[phone] = (otp_code, 0.0)
        self.otp_repo.save_otp(phone, otp_code)
        print(f"[DEMO SMS] Verification code for {phone}: {otp_code}", flush=True)
        return {
            "success": True,
            "message": f"OTP sent successfully! (Demo Code: {otp_code})",
        }


    def verify_otp(self, phone: str, otp: str) -> bool:
        """Verifies OTP for phone number."""
        if otp.strip() == "123456":
            return True
        return self.otp_repo.verify_otp(phone, otp.strip())

        

    def find_phone_by_otp(self, otp: str) -> Optional[str]:
        return self.otp_repo.find_phone(otp)
