import os
import uuid

from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile, Header
from fastapi.responses import FileResponse

from . import config, storage
from .models import AlarmIn, AlarmOut, ImageOut, MessageIn, MessageOut

app = FastAPI(title="buddymessanger")

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_IMAGE_BYTES = 20 * 1024 * 1024  # 20 MB


@app.on_event("startup")
def on_startup() -> None:
    storage.init_db()
    os.makedirs(config.IMAGES_DIR, exist_ok=True)


def require_auth(authorization: str | None = Header(default=None)) -> None:
    expected = f"Bearer {config.TOKEN}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="invalid or missing token")


def _row_to_message(row) -> MessageOut:
    return MessageOut(**dict(row))


def _row_to_alarm(row) -> AlarmOut:
    data = dict(row)
    data["delivered"] = bool(data["delivered"])
    return AlarmOut(**data)


def _row_to_image(row) -> ImageOut:
    return ImageOut(**dict(row))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/messages", response_model=MessageOut, dependencies=[Depends(require_auth)])
def post_message(payload: MessageIn):
    row = storage.add_message(payload.sender, payload.text)
    return _row_to_message(row)


@app.get("/messages", response_model=list[MessageOut], dependencies=[Depends(require_auth)])
def get_messages(since_id: int = 0, sender: str | None = None):
    rows = storage.list_messages(since_id, sender)
    return [_row_to_message(r) for r in rows]


@app.post("/alarms", response_model=AlarmOut, dependencies=[Depends(require_auth)])
def post_alarm(payload: AlarmIn):
    row = storage.add_alarm(payload.title, payload.message, payload.sound)
    return _row_to_alarm(row)


@app.get("/alarms", response_model=list[AlarmOut], dependencies=[Depends(require_auth)])
def get_alarms(since_id: int = 0):
    rows = storage.list_alarms(since_id)
    return [_row_to_alarm(r) for r in rows]


@app.post("/alarms/{alarm_id}/ack", dependencies=[Depends(require_auth)])
def ack_alarm(alarm_id: int):
    storage.ack_alarm(alarm_id)
    return {"status": "ok"}


@app.post("/images", response_model=ImageOut, dependencies=[Depends(require_auth)])
async def post_image(
    file: UploadFile,
    sender: str = Form(...),
    caption: str | None = Form(default=None),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="unsupported image type")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="image too large")

    stored_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(config.IMAGES_DIR, stored_name)
    with open(dest_path, "wb") as f:
        f.write(contents)

    row = storage.add_image(sender, stored_name, caption)
    return _row_to_image(row)


@app.get("/images", response_model=list[ImageOut], dependencies=[Depends(require_auth)])
def get_images(since_id: int = 0):
    rows = storage.list_images(since_id)
    return [_row_to_image(r) for r in rows]


@app.get("/images/{image_id}/file", dependencies=[Depends(require_auth)])
def get_image_file(image_id: int):
    row = storage.get_image(image_id)
    if row is None:
        raise HTTPException(status_code=404, detail="image not found")
    path = os.path.join(config.IMAGES_DIR, row["filename"])
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="image file missing on disk")
    return FileResponse(path)
