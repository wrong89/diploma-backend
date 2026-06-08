from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.enum import ChatRoles, ChatType
from src.models import Chat, ChatMember, User


def create_chat(db: Session, type: str, address: str | None, title: str):
    new_chat = Chat(type=type, address=address, title=title)

    db.add(new_chat)
    db.flush()

    return new_chat


def get_chat_by_id(db: Session, id: int) -> Chat | None:
    return db.query(Chat).filter(Chat.id == id).scalar()


def get_chat_by_address(db: Session, address: str) -> Chat | None:
    return db.query(Chat).filter(Chat.address == address).scalar()


def user_is_chat_member(db: Session, chat_id: int, user_id: int) -> bool:
    is_member = (
        db.query(ChatMember)
        .filter(ChatMember.chat_id == chat_id, ChatMember.user_id == user_id)
        .scalar()
    )

    if is_member is not None:
        return True
    return False


# Checks for service
def join_chat(
    db: Session,
    chat_id: int,
    user_id: int,
    role: str = ChatRoles.USER,
) -> ChatMember | None:
    new_member = ChatMember(chat_id=chat_id, user_id=user_id, role=role)
    db.add(new_member)
    db.flush()

    return new_member


def get_user_member_chats(db: Session, user_id: int) -> List[ChatMember]:
    return db.query(ChatMember).filter(ChatMember.user_id == user_id).all()


def get_user_chats(db: Session, user_id: int) -> List[Chat]:
    member_chats = get_user_member_chats(db, user_id)

    user_chats = []

    for member_chat in member_chats:
        chat = get_chat_by_id(db, member_chat.chat_id)
        user_chats.append(chat)

    return user_chats


def get_other_chat_member(
    db: Session,
    chat_id: int,
    current_user_id: int,
) -> User | None:
    return (
        db.query(User)
        .join(ChatMember, ChatMember.user_id == User.id)
        .filter(ChatMember.chat_id == chat_id)
        .filter(User.id != current_user_id)
        .first()
    )


def update_last_read_msg_id(db: Session, chat_id: int, last_read_msg_id: int) -> int:
    db.query(ChatMember).filter(ChatMember.chat_id == chat_id).update(
        {"last_read_msg_id": last_read_msg_id}
    )
    return last_read_msg_id


def leave_chat(db: Session, chat_id: int, user_id: int):
    db.query(ChatMember).filter(
        ChatMember.chat_id == chat_id, ChatMember.user_id == user_id
    ).delete()


# TODO: pagination
def search_chats_by_title(db: Session, query: str) -> List[Chat]:
    return db.query(Chat).filter(Chat.title.ilike(f"%{query}%")).all()


def search_chats_by_query(db: Session, query: str) -> List[Chat]:
    print("[SEARCH CHATS BY QUERY]", query)
    if query[0] != "@":
        return search_chats_by_title(db, query)

    print(query[1:])
    chat = get_chat_by_address(db, query[1:])

    if chat:
        return [chat]
    return []


def user_is_banned(db: Session, chat_id: int, user_id: int) -> bool:
    banned: ChatMember | None = (
        db.query(ChatMember)
        .filter(ChatMember.chat_id == chat_id, ChatMember.user_id == user_id)
        .scalar()
    )

    if banned is not None:
        return banned.is_banned
    return False


def get_chat_members_count(db: Session, chat_id: int) -> int:
    return db.query(ChatMember).filter(ChatMember.chat_id == chat_id).count()


def can_user_send_message(db: Session, chat_id: int, user_id: int) -> bool:
    chat_member = get_chat_member(db, chat_id, user_id)

    if not chat_member:
        return False

    return chat_member.role == ChatRoles.USER or chat_member.role == ChatRoles.ADMIN


def get_chat_member(db: Session, chat_id: int, user_id: int) -> ChatMember | None:
    return (
        db.query(ChatMember)
        .filter(ChatMember.chat_id == chat_id, ChatMember.user_id == user_id)
        .scalar()
    )


def get_private_chat_between_users(
    db: Session, user1_id: int, user2_id: int
) -> Chat | None:
    chat = (
        db.query(Chat)
        .join(ChatMember)
        .filter(Chat.type == ChatType.PRIVATE)
        .filter(ChatMember.user_id.in_([user1_id, user2_id]))
        .group_by(Chat.id)
        .having(func.count(ChatMember.user_id) == 2)
        .first()
    )

    return chat


def get_private_chat_title(
    db: Session, chat_id: int, origin_user_id: int
) -> int | None:
    chat_member = (
        db.query(ChatMember)
        .filter(ChatMember.chat_id == chat_id, ChatMember.user_id != origin_user_id)
        .first()
    )
    if not chat_member:
        return None

    return chat_member.user_id
