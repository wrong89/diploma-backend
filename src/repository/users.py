from sqlalchemy.orm import Session

from src.models import User


def get_user_by_login(db: Session, login: str) -> User | None:
    return db.query(User).filter(User.login == login).scalar()


def get_user_by_id(db: Session, id: int) -> User | None:
    return db.query(User).filter(User.id == id).scalar()


def create_user(
    db: Session,
    login: str,
    name: str,
    password: str,
    phone: str,
    email: str,
) -> User:
    user = User(
        login=login,
        name=name,
        password_hash=password,
        phone=phone,
        email=email,
    )
    db.add(user)
    db.flush()
    return user
