from enum import StrEnum, auto


class ChatType(StrEnum):
    PRIVATE = auto()
    GROUP = auto()
    CHANNEL = auto()


class ChatRoles(StrEnum):
    ADMIN = auto()  # READ-WRITE-BAN-DELETE
    USER = auto()  # READ-WRITE
    READER = auto()  # READ-ONLY
