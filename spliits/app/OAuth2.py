from fastapi import Depends
import jwt
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError
from app import db,models
from sqlalchemy.orm import session


load_dotenv()

secret_key=os.getenv('SECRET_KEY')
algorithm=os.getenv('ALGORITHM')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")




def get_current_user(token: str = Depends(oauth2_scheme), db: session = Depends(db.get_db)):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise 
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise 
        return user
    except InvalidTokenError:
        raise 
