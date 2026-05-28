from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserSchema(BaseModel):
    id: int
    name: str
    login: str
    phone: PhoneNumber
    email: EmailStr

    class Config:
        from_attributes = True


class CreateUserSchema(BaseModel):
    login: str = Field(..., max_length=127)
    name: str
    password: str
    phone: PhoneNumber
    email: EmailStr

    @field_validator("login", "name", "password")
    def check_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be empty or blank")
        return value


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

    @field_validator("type", "title")
    def check_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be empty or blank")
        return value


class ChatMemberSchema(BaseModel):
    role: str
    is_banned: bool
    joined_at: datetime

    class Config:
        from_attributes = True


class ChatFollowersCount(BaseModel):
    chat_id: int
    followers: int


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
