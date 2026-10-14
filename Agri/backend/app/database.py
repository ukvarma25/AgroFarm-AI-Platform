from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.app.config import BACKEND_DIR, settings


def _engine_url() -> str:
    url = settings.database_url
    if url.startswith("sqlite:///./"):
        db_path = (BACKEND_DIR / url.replace("sqlite:///./", "")).resolve()
        return f"sqlite:///{db_path.as_posix()}"
    return url


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(_engine_url(), connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
