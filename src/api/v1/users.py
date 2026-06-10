import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from dependency import get_current_user, get_db
from src import auth
from src.models import User
from src.repository import users as users_repository
from src.schemas import CreateUserSchema, Token, UserSchema
from src.utils import UPLOAD_DIR

router = APIRouter()


@router.post("/users", response_model=UserSchema)
def create_user(payload: CreateUserSchema, db: Session = Depends(get_db)) -> UserSchema:
    if users_repository.get_user_by_login(db, payload.login):
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    new_user = users_repository.create_user(
        db, payload.login, payload.name, payload.password
    )

    db.commit()

    return UserSchema.model_validate(new_user)


@router.post("/register", response_model=UserSchema)
async def register(
    login: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    avatar: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> UserSchema:
    if users_repository.get_user_by_login(db, login):
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    hashed_password = auth.get_password_hash(password)

    avatar_path = None

    new_user = users_repository.create_user(
        db,
        login,
        name,
        hashed_password,
        phone,
        email,
    )

    if avatar:
        ext = avatar.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        file_path = UPLOAD_DIR / filename

        with open(file_path, "wb") as buffer:
            buffer.write(await avatar.read())

        avatar_path = f"/static/avatars/{filename}"
        new_user.avatar_path = avatar_path

    db.commit()
    db.refresh(new_user)

    return UserSchema.model_validate(new_user)


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = users_repository.get_user_by_login(db, form_data.username)

    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": user.login, "uid": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/name/{user_id}", response_model=UserSchema)
async def read_user_name(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    user = users_repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    return UserSchema.model_validate(user)


@router.get("/{login}", response_model=UserSchema)
async def get_user_by_login(
    login: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    user = users_repository.get_user_by_login(db, login)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with {login} is not found",
        )

    return UserSchema.model_validate(user)
