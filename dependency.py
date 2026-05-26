from typing import Generator

from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPBearer,
    OAuth2PasswordBearer,
)
from sqlalchemy.orm import Session

from src import auth
from src.database import SessionLocal
from src.repository import users as users_repository

security = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(get_db),
# ) -> User:
#     credentials_exception = HTTPException(
#         status_code=401,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     try:
#         payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])

#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception

#     except JWTError:
#         raise credentials_exception

#     user = users_repository.get_user_by_id(db, user_id)
#     if user is None:
#         raise credentials_exception

#     return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    username = auth.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = users_repository.get_user_by_login(db, username)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
