def normalize_phone(phone: str) -> str | None:
    """Return a Sri Lankan phone number in E.164 format."""
    digits = "".join(char for char in phone if char.isdigit())
    if len(digits) == 11 and digits.startswith("94"):
        national_number = digits[2:]
    elif len(digits) == 10 and digits.startswith("0"):
        national_number = digits[1:]
    elif len(digits) == 9:
        national_number = digits
    else:
        return None
    return f"+94{national_number}"
