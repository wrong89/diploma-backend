from pathlib import Path

from src.enum import ChatType
from src.models import Chat, User

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "avatars"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

CHAT_UPLOAD_DIR = Path("static/chat_avatars")
CHAT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def make_chat_from_user(user: User) -> Chat:
    chat_from_user = Chat(
        id=user.id,
        type=ChatType.PRIVATE,
        title=user.name,
        address=user.login,
        created_at=user.created_at,
        avatar_path=user.avatar_path,
    )
    print("make chat from user", chat_from_user.avatar_path)

    return chat_from_user
