from src.enum import ChatType
from src.models import Chat, User


def make_chat_from_user(user: User) -> Chat:
    chat_from_user = Chat(
        id=user.id,
        type=ChatType.PRIVATE,
        title=user.name,
        address=user.login,
        created_at=user.created_at,
    )

    return chat_from_user
