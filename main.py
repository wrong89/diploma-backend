import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.chats import router as chats_router
from src.api.v1.messages import router as messages_router
from src.api.v1.users import router as users_router
from src.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(chats_router, prefix="/api/v1/chats", tags=["chats"])
app.include_router(messages_router, prefix="/api/v1/messages", tags=["messages"])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    uvicorn.run("main:app", reload=True)


if __name__ == "__main__":
    main()
