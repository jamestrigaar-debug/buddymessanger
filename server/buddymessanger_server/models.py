from pydantic import BaseModel


class MessageIn(BaseModel):
    sender: str
    text: str


class MessageOut(BaseModel):
    id: int
    sender: str
    text: str
    created_at: float


class AlarmIn(BaseModel):
    title: str
    message: str
    sound: str | None = None


class AlarmOut(BaseModel):
    id: int
    title: str
    message: str
    sound: str | None
    created_at: float
    delivered: bool


class ImageOut(BaseModel):
    id: int
    sender: str
    filename: str
    caption: str | None
    created_at: float
