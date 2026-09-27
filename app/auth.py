import hashlib
import secrets
import re


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def validate_email(email: str) -> bool:
    return bool(
        EMAIL_PATTERN.match(email)
    )


def hash_password(password: str) -> str:

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    )

    return (
        f"{salt}${password_hash.hex()}"
    )


def verify_password(
    password: str,
    stored_hash: str
) -> bool:

    try:

        salt, original_hash = (
            stored_hash.split("$")
        )

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000
        )

        return secrets.compare_digest(
            password_hash.hex(),
            original_hash
        )

    except ValueError:
        return False