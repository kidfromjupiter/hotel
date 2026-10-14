from app.phone import normalize_phone


def test_phone_formats_share_one_string_representation():
    assert normalize_phone("0771234567") == "+94771234567"
    assert normalize_phone("+94 77 123 4567") == "+94771234567"
    assert normalize_phone("771234567") == "+94771234567"


def test_invalid_phone_is_rejected():
    assert normalize_phone("") is None
    assert normalize_phone("12345") is None
