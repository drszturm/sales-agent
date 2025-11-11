from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Change to your database URL

# SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:5432/{settings.DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
