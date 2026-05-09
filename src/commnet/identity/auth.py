from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
from dataclasses import dataclass
from typing import Any

USERNAME_RE = re.compile(r'^[A-Za-z0-9_.-]{3,32}$')
PBKDF2_ITERATIONS = 150_000
PASSWORD_SCHEME = 'pbkdf2_sha256'


class AuthInputError(ValueError):
    pass


def validate_username(username: str) -> str:
    username = (username or '').strip()
    if not USERNAME_RE.match(username):
        raise AuthInputError('Username must be 3-32 characters using letters, numbers, underscore, hyphen, or period.')
    return username.lower()


def validate_display_name(display_name: str) -> str:
    display_name = (display_name or '').strip()
    if not (1 <= len(display_name) <= 64):
        raise AuthInputError('Display name must be 1-64 characters.')
    return display_name


def validate_password(password: str) -> str:
    password = password or ''
    if not (8 <= len(password) <= 128):
        raise AuthInputError('Password must be 8-128 characters.')
    return password


def validate_hint(hint: str, password: str = '') -> str:
    hint = (hint or '').strip()
    if len(hint) > 160:
        raise AuthInputError('Password hint must be 160 characters or fewer.')
    if hint and password and hint.lower() == password.lower():
        raise AuthInputError('Password hint cannot equal the password.')
    return hint


def hash_password(password: str, salt: bytes | None = None, iterations: int = PBKDF2_ITERATIONS) -> dict[str, Any]:
    validate_password(password)
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return {
        'scheme': PASSWORD_SCHEME,
        'iterations': iterations,
        'salt_hex': salt.hex(),
        'hash_hex': digest.hex(),
    }


def verify_password(password: str, salt_hex: str, hash_hex: str, iterations: int) -> bool:
    try:
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac('sha256', (password or '').encode('utf-8'), salt, int(iterations))
    return hmac.compare_digest(digest, expected)


def new_session_id() -> str:
    return 'sess_' + secrets.token_urlsafe(32)
