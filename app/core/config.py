import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
DB_PATH = BASE_DIR / "finctrl.db"

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

SYNTHETIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

class AppConfig(BaseModel):
    app_name: str = "FINCTRL AI"
    tagline: str = "Reconcile. Investigate. Forecast. Control."
    db_path: str = str(DB_PATH)
    ollama_model: str = DEFAULT_MODEL
    ollama_host: str = OLLAMA_HOST
    demo_seed: int = 42

config = AppConfig()
