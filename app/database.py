# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Uses environment variable DATABASE_URL; default for local testing if not set.
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://faceuser:facepass@localhost:5432/facerec')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
