from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass

load_dotenv()

url=os.getenv('DATABASE_URL1')


engine = create_engine(url)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


