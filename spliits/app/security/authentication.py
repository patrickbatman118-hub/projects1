from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from app import app,db,models,schemas
from sqlalchemy.orm import session
import bcrypt
router = APIRouter(tags=['authentication'])
from jose import jwt
from datetime import timedelta,timezone,datetime
import os
from dotenv import load_dotenv
load_dotenv()

secret_key=os.getenv('SECRET_KEY')
algorithm=os.getenv('ALGORITHM')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": 'access'})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=15)
    to_encode.update({"exp": expire, "type": 'refresh'})
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
        app.logger.info(f'User disabled: {user.id}')
        raise app.InvalidCredentials
    if not bcrypt.checkpw(request.password.encode(),user.password.encode()):
        app.logger.warning(f'Invalid Password: {request.username}')
        raise app.InvalidCredentials
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.post('/refersh_token')
def refersh_token(refresh_token: str):
    payload = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
    if not payload['type'] != 'refresh':
        app.logger.warning(f'Invalid Token: {refresh_token}')
        raise app.InvalidCredentials
    user_id = payload['sub']
    access_token = create_access_token(data={"sub": user_id})
    return {'acces_token': access_token, 'token_type': 'bearer'}


# @router.post("/signout")
# async def signout(token: str ):
#     # 1. Decode the token to get the jti (unique ID)
#     payload = jwt.decode(token, secret_key, algorithms=[algorithm])
#     jti = payload.get("jti")
    
#     # 2. Add this jti to your Redis Denylist/Blacklist
#     # This ensures that even if someone has the token, it won't work anymore
#     await redis.setex(f"blacklist:{jti}", TOKEN_EXPIRES_IN, "revoked")
    
#     return {"message": "Successfully signed out"}

