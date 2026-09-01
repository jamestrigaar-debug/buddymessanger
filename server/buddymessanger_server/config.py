import os


def _load_dotenv(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

TOKEN = os.environ.get("BUDDY_TOKEN", "")
HOST = os.environ.get("BUDDY_HOST", "0.0.0.0")
PORT = int(os.environ.get("BUDDY_PORT", "8765"))
DB_PATH = os.environ.get("BUDDY_DB_PATH", "./buddymessanger.db")
IMAGES_DIR = os.environ.get("BUDDY_IMAGES_DIR", "./images")

if not TOKEN:
    raise RuntimeError(
        "BUDDY_TOKEN is not set. Copy server/.env.example to server/.env "
        "and set a long random secret before starting the server."
    )
