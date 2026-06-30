from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .core.config import settings

import os

# Konfigurasi khusus Aiven (SSL)
connect_args = {}
ca_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ca.pem")
if os.path.exists(ca_path):
    connect_args["ssl"] = {"ca": ca_path}

engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()