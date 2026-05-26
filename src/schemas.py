from datetime import datetime

from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    id: int
    name: str
    login: str

    class Config:
        from_attributes = True


class CreateUserSchema(BaseModel):
    login: str = Field(..., max_length=127)
    name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Chat Schemas


class ChatSchema(BaseModel):
    id: int
    type: str
    address: str | None
    created_at: datetime
    title: str

    class Config:
        from_attributes = True


class CreateChatSchema(BaseModel):
    type: str
    title: str
    address: str | None


class ChatMemberSchema(BaseModel):
    role: str
    is_banned: bool
    joined_at: datetime

    class Config:
        from_attributes = True


# Message Schemas


class MessageSchema(BaseModel):
    id: int
    chat_id: int
    author_user_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True


class CreateMessageSchema(BaseModel):
    chat_id: int
    text: str
