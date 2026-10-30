import pytest
from jose import jwt
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)

def test_password_hashing_and_verification():
    password = "CorrectHorseBatteryStaple123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_bcrypt_72_byte_truncation():
    # Passing > 72 bytes must NOT raise ValueError
    super_long_password = "A" * 150
    hashed = hash_password(super_long_password)
    assert verify_password(super_long_password, hashed) is True

def test_jwt_token_payload():
    user_id = 99
    token = create_access_token({"sub": str(user_id)})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == str(user_id)
    assert "exp" in payload