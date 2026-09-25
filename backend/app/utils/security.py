"""Password hashing.

Werkzeug defaults to scrypt, which is memory-hard and needs no native
dependency. Swapping algorithms later touches only these two functions.
"""

from __future__ import annotations

from werkzeug.security import check_password_hash, generate_password_hash

HASH_METHOD = "scrypt"


def hash_password(plain_password: str) -> str:
    return generate_password_hash(plain_password, method=HASH_METHOD)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, plain_password)
