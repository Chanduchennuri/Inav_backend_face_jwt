import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

USERS_DIR = BASE_DIR / "data" / "users"

USERS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def normalize_user_id(
    user_id: str
) -> str:

    return (
        user_id
        .strip()
        .lower()
        .replace(" ", "_")
    )


def user_path(user_id: str) -> Path:

    user_id = normalize_user_id(
        user_id
    )

    return USERS_DIR / f"{user_id}.json"


def user_exists(user_id: str) -> bool:

    return user_path(user_id).exists()


def save_user(user: dict):

    path = user_path(
        user["user_id"]
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            user,
            file,
            indent=4
        )


def get_user(user_id: str):

    path = user_path(user_id)

    if not path.exists():
        return None

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)