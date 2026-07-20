from fastapi import Depends, HTTPException
from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from app import db,models,app
from sqlalchemy.orm import session
from uuid import UUID
from ..models.jwt import revoked_tokens
import redis
import redis.exceptions
load_dotenv()

secret_key=os.getenv('SECRET_KEY')
algorithm=os.getenv('ALGORITHM')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

def revoke_jti(jti: str, remaining_seconds: int):
    try:
        redis_client.set(f"revoked:{jti}", "1", ex=remaining_seconds)
    except redis.exceptions.ConnectionError:
        app.logger.critical("Redis unreachable during revocation")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except redis.exceptions.TimeoutError:
        app.logger.error("Redis timeout during revocation")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

def is_revoked(jti: str) -> bool:
    try:
        return redis_client.exists(f"revoked:{jti}") == 1
    except redis.exceptions.ConnectionError:
        app.logger.critical("Redis unreachable during revocation check")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except redis.exceptions.TimeoutError:
        app.logger.error("Redis timeout during revocation check")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


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
        jti = payload["jti"]
        if is_revoked(jti):
            app.logger.warning(f'revoked_token: jti={jti}')
            raise HTTPException(status_code=401, detail="Token has been revoked")
        user = db.query(models.users.User).filter(models.users.User.user_id == UUID(user_id)).first()
        if user is None:
            app.logger.warning('No User Exists')
            raise app.InvalidCredentials
        if user.disabled:
            app.logger.info(f'User disabled: {user.user_id}')
            raise app.InvalidCredentials
        if is_revoked:
            app.logger.warning(f"rejected token: revoked jti={jti}")
            raise HTTPException(status_code=401, detail="Token has been revoked")
        return CurrentUser(payload)
    except (HTTPException,app.InvalidCredentials):
        raise    
    except JWTError as e: 
        app.logger.warning('Token is invalid or expired: {e}')
        raise app.InvalidCredentials  
    except Exception:
        app.logger.exception('failed to get user')
        raise HTTPException(status_code=500, detail='Error getting user')

def get_current_active_user1(payload = Depends(get_current_user), db: session = Depends(db.get_db)):
    user_id = payload.user_id
    user = db.query(models.users.User).filter(models.users.User.user_id == user_id).first()
    return user

def get_current_active_user(
    current_user = Depends(get_current_active_user1)
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



