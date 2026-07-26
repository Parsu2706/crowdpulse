from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings): 
    APP_NAME : str = "CrowdPulse"
    VERSION : str = "1.0.0"

    BASE_DIR : Path = Path(__file__).resolve().parent.parent
    DATA_DIR : Path = Path(__file__).resolve().parent.parent / 'data'
    GROQ_API_KEY:    str | None = None
    GEMINI_API_KEY:  str | None = None 
    NEWS_API_KEY : str | None = None

    REDDIT_CLIENT_ID : str | None = None
    REDDIT_CLIENT_SECRET : str | None = None
    REDDIT_USERNAME : str | None = None
    REDDIT_PASSWORD : str | None = None
    USER_AGENT : str = "Crowd"

    REDIS_URL : str = "redis://localhost:6379"

    class Config: 
        env_file = ".env"
        extra = "ignore"

settings = Settings()

DATA_RAW = settings.DATA_DIR / "raw"
NEWS_CSV = DATA_RAW / "news_latest.csv"
REDDIT_CSV = DATA_RAW  / "reddit_latest.csv"
SNAPSHOTS_DIR = settings.DATA_DIR / "snapshots"

DATA_RAW.mkdir(parents=True , exist_ok=True)
SNAPSHOTS_DIR.mkdir(parents=True , exist_ok=True)

