import pytest
from pydantic import ValidationError

from app.schemas.auth import GuestLoginRequest, RegisterRequest


def _register(**overrides):
    data = {"email": "a@b.com", "name": "Alice", "password": "abcdefg1"}
    data.update(overrides)
    return RegisterRequest(**data)


def test_register_accepts_valid_payload():
    assert _register().name == "Alice"


def test_register_rejects_password_over_72_bytes():
    # 40 two-byte characters: under 128 characters but 80 bytes, which bcrypt cannot hash
    with pytest.raises(ValidationError):
        _register(password="é" * 39 + "a1")


def test_register_rejects_empty_or_long_name():
    with pytest.raises(ValidationError):
        _register(name="")
    with pytest.raises(ValidationError):
        _register(name="x" * 65)


def test_guest_login_rejects_short_device_id():
    with pytest.raises(ValidationError):
        GuestLoginRequest(device_id="abc")
