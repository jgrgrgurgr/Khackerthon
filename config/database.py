from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = "sqlite:///./stk_trd.db"

eng = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)
Base = declarative_base()

def get_db():
    db = SessLocal()
    try:
        yield db
    finally:
        db.close()