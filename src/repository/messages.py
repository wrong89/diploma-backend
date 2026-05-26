from sqlalchemy.orm import Session

from src.models import Message


# todo: rename author_user_id to author_id OR user_id
def create_message(
    db: Session, chat_id: int, author_user_id: int, text: str
) -> Message:
    msg = Message(
        chat_id=chat_id,
        author_user_id=author_user_id,
        text=text,
    )

    db.add(msg)
    db.flush()
    return msg


def get_message_by_id(db: Session, id: int) -> Message | None:
    return db.query(Message).filter(Message.id == id).scalar()


def get_chat_messages(db: Session, chat_id: int) -> list[Message]:
    return db.query(Message).filter(Message.chat_id == chat_id).all()


def get_chat_last_message(db: Session, chat_id: int) -> Message | None:
    return (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.id.desc())
        .first()
    )
