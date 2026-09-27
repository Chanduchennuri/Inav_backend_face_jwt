import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv


load_dotenv()


JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "dev-secret"
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

JWT_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_EXPIRE_MINUTES",
        "5"
    )
)


def create_access_token(
    user_id: str,
    name: str
) -> str:

    now = datetime.now(timezone.utc)

    expires_at = (
        now +
        timedelta(
            minutes=JWT_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": user_id,
        "name": name,
        "iat": now,
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(
    token: str
):

    try:

        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

    except jwt.ExpiredSignatureError:

        return None

    except jwt.InvalidTokenError:

        return None