from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependency import get_current_user, get_db
from src.enum import ChatRoles, ChatType
from src.models import User
from src.repository import chats as chats_repository
from src.repository import users as users_repository
from src.schemas import (
    ChatMemberSchema,
    ChatSchema,
    CreateChatSchema,
)
from src.utils import make_chat_from_user

router = APIRouter()


@router.post("/", response_model=ChatSchema)
def create_chat(
    payload: CreateChatSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatSchema:
    if payload.address and chats_repository.get_chat_by_address(db, payload.address):
        raise HTTPException(
            status_code=400,
            detail="Chat already exists",
        )

    new_chat = chats_repository.create_chat(
        db,
        payload.type,
        payload.address,
        payload.title,
    )

    chats_repository.join_chat(db, new_chat.id, current_user.id, ChatRoles.ADMIN)
    db.commit()

    return ChatSchema.model_validate(new_chat)


@router.get(
    "/direct/{target_user_id}",
    response_model=ChatSchema,
)
def get_or_create_private_chat(
    target_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatSchema:
    existing = chats_repository.get_private_chat_between_users(
        db, current_user.id, target_user_id
    )

    if existing:
        return ChatSchema.model_validate(existing)

    target_user = users_repository.get_user_by_id(db, target_user_id)

    chat = chats_repository.create_chat(
        db,
        ChatType.PRIVATE,
        None,
        "Direct",
    )

    chats_repository.join_chat(db, chat.id, current_user.id, ChatRoles.ADMIN)
    chats_repository.join_chat(db, chat.id, target_user_id, ChatRoles.ADMIN)

    db.commit()

    return ChatSchema.model_validate(chat)


@router.post("/join/{chat_id}", response_model=ChatSchema)
def join_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatSchema:
    current_chat = chats_repository.get_chat_by_id(db, chat_id)
    if current_chat is None:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )

    if chats_repository.user_is_chat_member(db, chat_id, current_user.id):
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this chat",
        )

    if current_chat.type == ChatType.CHANNEL:
        chat_member = chats_repository.join_chat(
            db,
            chat_id,
            current_user.id,
            ChatRoles.READER,
        )
    else:  # todo: refactor it
        chat_member = chats_repository.join_chat(
            db,
            chat_id,
            current_user.id,
        )

    db.commit()

    joined_chat = chats_repository.get_chat_by_id(db, chat_member.chat_id)

    return ChatSchema.model_validate(joined_chat)


# @router.get("/", response_model=List[ChatSchema])
# def get_my_chats(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ) -> List[ChatSchema]:
#     # Useless function get_user_chats.
#     # TODO: Remove it and change to get_user_member_chats
#     return chats_repository.get_user_chats(db, current_user.id)


@router.get("/", response_model=List[ChatSchema])
def get_my_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ChatSchema]:
    chats = chats_repository.get_user_chats(db, current_user.id)

    result = []

    for chat in chats:
        chat_data = ChatSchema.model_validate(chat)

        if chat.type == ChatType.PRIVATE:
            other_user = chats_repository.get_other_chat_member(
                db,
                chat.id,
                current_user.id,
            )

            if other_user:
                chat_data.title = other_user.name

        result.append(chat_data)

    return result


@router.get("/search/{query}", response_model=List[ChatSchema])
def search_chats(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ChatSchema]:
    if query[0] == "@" and query[1:] != current_user.login:
        query = query[1:]
        print("QUERY[]", query)

        user = users_repository.get_user_by_login(db, query)
        if user:
            chat_from_user = make_chat_from_user(user)
            print("[CHAT FROM USER]", chat_from_user)

            return [chat_from_user]
    return chats_repository.search_chats_by_query(db, query)


@router.get("/{chat_id}", response_model=ChatSchema)
def get_chat_by_id(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = chats_repository.get_chat_by_id(db, chat_id)

    if chat.type == ChatType.PRIVATE:
        chat.title = ""
        opposite_user_id = chats_repository.get_private_chat_title(
            db,
            chat_id,
            current_user.id,
        )

        user = users_repository.get_user_by_id(db, opposite_user_id)
        if user:
            chat.title = user.name

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )

    return ChatSchema.model_validate(chat)


@router.get("/by-address/{address}", response_model=ChatSchema)
def get_chat_by_address(
    address: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatSchema:
    chat = chats_repository.get_chat_by_address(db, address)

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )

    return ChatSchema.model_validate(chat)


@router.delete("/{chat_id}")
def leave_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if chats_repository.get_chat_by_id(db, chat_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )

    if not chats_repository.user_is_chat_member(db, chat_id, current_user.id):
        raise HTTPException(
            status_code=400,
            detail="User is not a member of this chat",
        )

    chats_repository.leave_chat(db, chat_id, current_user.id)
    db.commit()

    return {"chat_id": chat_id}


@router.get("/member/{chat_id}", response_model=ChatMemberSchema)
def get_chat_member(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatMemberSchema:
    if not chats_repository.user_is_chat_member(db, chat_id, current_user.id):
        return ChatMemberSchema(
            role="not_member",
            is_banned=False,
            joined_at=datetime.now(),
        )

    chat_member = chats_repository.get_chat_member(
        db,
        chat_id,
        current_user.id,
    )
    if not chat_member:
        raise HTTPException(
            status_code=404,
            detail="Chat member not found",
        )
    return ChatMemberSchema.model_validate(chat_member)


@router.get("/{chat_id}/followers/count")
def get_followers_count(
    chat_id: int,
    db: Session = Depends(get_db),
):
    count = chats_repository.get_chat_members_count(db, chat_id)
    return {
        "followers": count,
        "chat_id": chat_id,
    }
