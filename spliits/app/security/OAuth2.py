from fastapi import Depends, HTTPException
from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from app import db,models,app
from sqlalchemy.orm import session
from uuid import UUID
from ..models.jwt import revoked_tokens
load_dotenv()

secret_key=os.getenv('SECRET_KEY')
algorithm=os.getenv('ALGORITHM')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class CurrentUser:
    def __init__(self, payload: dict):
        self.user_id = UUID(payload["sub"])
        self.scopes = payload["scopes"]
        self.jti = payload["jti"]

    def has_scope(self, scope: str):
        return scope in self.scopes


def get_current_user(token: str = Depends(oauth2_scheme), db: session = Depends(db.get_db)):
    try:     
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            app.logger.warning('No User Exists')
            raise app.InvalidCredentials
        user = db.query(models.users.User).filter(models.users.User.user_id == UUID(user_id)).first()
        if user is None:
            app.logger.warning('No User Exists')
            raise app.InvalidCredentials
        if user.disabled:
            app.logger.info(f'User disabled: {user.user_id}')
            raise app.InvalidCredentials
        jti = payload["jti"]
        is_revoked = db.query(revoked_tokens).filter(revoked_tokens.jti == UUID(jti)).first()
        if is_revoked:
            app.logger.warning(f"rejected token: revoked jti={jti}")
            raise HTTPException(status_code=401, detail="Token has been revoked")
        return CurrentUser(payload)
        
    except JWTError as e: 
        app.logger.warning('Token is invalid or expired: {e}')
        raise app.InvalidCredentials  
    except Exception:
        db.rollback()
        app.logger.exception('failed to get user')
        raise HTTPException(status_code=500, detail='Error getting user')

def get_current_active_user1(payload = Depends(get_current_user)):
    user_id = payload.user_id
    user = db.query(models.users.User).filter(models.users.User.user_id == UUID(user_id)).first()
    return user

def get_current_active_user(
    current_user = Depends(get_current_active_user1)
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



