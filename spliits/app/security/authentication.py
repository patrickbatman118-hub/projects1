from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from app import app,db,models,schemas
from sqlalchemy.orm import session
import bcrypt
router = APIRouter(tags=['authentication'])
from jose import jwt,JWTError
from datetime import timedelta,timezone,datetime
import os
from dotenv import load_dotenv
load_dotenv()
import uuid
from ..models.jwt import revoked_tokens
from sqlalchemy.exc import IntegrityError
from .OAuth2 import get_current_active_user,revoke_jti
from ..models.users import User


secret_key=os.getenv('SECRET_KEY')
algorithm=os.getenv('ALGORITHM')

def build_scopes(user: User):
    scopes = ["user"]
    if user.is_admin:
        scopes.append("admin")
    return scopes

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=55)
    to_encode.update({"exp": expire, "type": 'access', 'jti': str(uuid.uuid4()), "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=15)
    to_encode.update({"exp": expire, "type": 'refresh', 'jti': str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


@router.get('/login')
def login(request: Request):
    if request.method == "GET":
        return {"message": "Return the HTML login form"}
    
@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: session = Depends(db.get_db)):
    user = db.query(models.users.User).filter(models.users.User.email == request.username).first()
    if not user:
        app.logger.warning(f'No User Exists: {request.username}')
        raise app.InvalidCredentials
    if user.disabled:
        app.logger.info(f'User disabled: {user.user_id}')
        raise app.InvalidCredentials
    if not bcrypt.checkpw(request.password.encode(),user.password.encode()):
        app.logger.warning(f'Invalid Password: {request.username}')
        raise app.InvalidCredentials
    scopes = build_scopes(user)
    access_token = create_access_token(data={"sub": str(user.user_id), "scopes": scopes})
    refresh_token = create_refresh_token(data={"sub": str(user.user_id)})
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.post('/refersh_token')
def refersh_token(refresh_token: str, db: session = Depends(db.get_db)):
    payload = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
    if not payload['type'] == 'refresh':
        app.logger.warning(f'Invalid Token: {refresh_token}')
        raise app.InvalidCredentials
    jti = payload["jti"]
    is_revoked = db.query(revoked_tokens).filter(revoked_tokens.jti == uuid.UUID(jti)).first()
    if is_revoked:
        app.logger.warning(f"rejected token: revoked jti={jti}")
        raise HTTPException(status_code=401, detail="Token has been revoked")
    user_id = payload['sub']
    access_token = create_access_token(data={"sub": user_id})
    return {'acces_token': access_token, 'token_type': 'bearer'}


@router.post("/logout")
def signout(access_token: str,refresh_token: str, response: Response,   db: session = Depends(db.get_db)):
    try:
        payload = jwt.decode(access_token, secret_key, algorithms=[algorithm])
        payload_refresh = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
        jti1 = (payload.get("jti"))
        jti2 = payload_refresh['jti']
        user_id = payload["sub"]
        now = datetime.now(timezone.utc)
        access_token_exp = max((int(payload['exp']- now).total_seconds()), 0)    
        revoke_jti(jti1, expires_in_seconds=access_token_exp)
        db.add(revoked_tokens(jti=jti2, user_id=user_id, reason="logout"))
        db.commit()
        app.logger.info(f"logout: user={user_id} jti1={uuid.UUID(jti1)} jti2={uuid.UUID(jti2)} revoked")
        response.delete_cookie(key="access_token")
        response.delete_cookie(key='refresh_token')
        return {"detail": "logged out"}
    except HTTPException:
        raise
    except JWTError as e:
        app.logger.warning(f"logout: invalid token {e}")
        raise app.InvalidCredentials
    except Exception:
        db.rollback()
        app.logger.exception(f"signout failed: user={payload.get('sub') if payload else 'unknown'}")
        raise HTTPException(status_code=500, detail="Error during logout")


