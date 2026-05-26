from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependency import get_current_user, get_db
from src.models import User
from src.repository import chats as chats_repository
from src.repository import messages as messages_repository
from src.schemas import CreateMessageSchema, MessageSchema

router = APIRouter()


@router.post("/", response_model=MessageSchema)
def create_message(
    payload: CreateMessageSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not chats_repository.get_chat_by_id(db, payload.chat_id):
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )
    if not chats_repository.user_is_chat_member(db, payload.chat_id, current_user.id):
        raise HTTPException(
            status_code=400,
            detail="User is not a member of this chat",
        )

    if chats_repository.user_is_banned(db, payload.chat_id, current_user.id):
        raise HTTPException(
            status_code=400,
            detail="User is banned in this chat",
        )
    if not chats_repository.can_user_send_message(db, payload.chat_id, current_user.id):
        raise HTTPException(
            status_code=400,
            detail="User is not allowed to send messages in this chat",
        )

    new_msg = messages_repository.create_message(
        db,
        payload.chat_id,
        current_user.id,
        payload.text,
    )

    db.commit()

    return MessageSchema.model_validate(new_msg)


@router.get("/{chat_id}", response_model=list[MessageSchema])
def get_chat_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[MessageSchema]:
    return messages_repository.get_chat_messages(db, chat_id)


@router.get("/last/{chat_id}", response_model=MessageSchema)
def get_chat_last_message(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageSchema:
    return messages_repository.get_chat_last_message(db, chat_id)
