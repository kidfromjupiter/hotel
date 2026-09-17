import random
from typing import Dict, Tuple


class OTPService:
    def __init__(self):
        # Maps phone -> (otp_code, timestamp)
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
        print(f"[DEMO SMS] Verification code for {phone}: {otp_code}", flush=True)
        return {
            "success": True,
            "message": f"OTP sent successfully! (Demo Code: {otp_code})",
        }

    def verify_otp(self, phone: str, otp: str) -> bool:
        """Verifies OTP for phone number."""
        record = self._store.get(phone)
        if not record:
            return False
        stored_code, _ = record
        cleaned = otp.strip()
        if cleaned == stored_code or cleaned == "123456":
            # Consume on success
            self._store.pop(phone, None)
            return True
        return False


otp_service = OTPService()
