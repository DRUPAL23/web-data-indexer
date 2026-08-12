from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def healthcheck():
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
