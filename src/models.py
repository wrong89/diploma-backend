import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.enum import ChatRoles, ChatType


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ChatType.PRIVATE
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


class ChatMember(Base):
    __tablename__ = "chat_members"

    role: Mapped[str] = mapped_column(String(32), default=ChatRoles.USER)

    chat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    joined_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    last_read_msg_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


# class Chat(Base):
#     __tablename__ = "chats"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

#     type: Mapped[str] = mapped_column(String(20), nullable=False)

#     address: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

#     created_at: Mapped[str] = mapped_column(
#         TIMESTAMP, server_default=text("current_timestamp")
#     )


# class ChatMember(Base):
#     __tablename__ = "chat_members"

#     role: Mapped[str] = mapped_column(String(32), default=ChatRoles.USER.value)

#     chat_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True
#     )

#     user_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
#     )

#     joined_at: Mapped[str] = mapped_column(
#         TIMESTAMP, server_default=text("current_timestamp")
#     )

#     is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

#     last_read_msg_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Message(Base):
    __tablename__ = "msgs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    chat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )

    author_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
