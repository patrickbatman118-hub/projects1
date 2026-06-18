from fastapi import Depends, HTTPException
from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from app import db,models,app
from sqlalchemy.orm import session


load_dotenv()

secret_key=os.getenv('SECRET_KEY')
algorithm=os.getenv('ALGORITHM')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")




def get_current_user(token: str = Depends(oauth2_scheme), db: session = Depends(db.get_db)):
    print(f"DEBUG: THE EXACT TOKEN IS: [{token}]")
    try:     
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            app.logger.warning('No User Exists')
            raise app.InvalidCredentials
        user = db.query(models.users.User).filter(models.users.User.id == int(user_id)).first()
        if user is None:
            app.logger.warning('No User Exists')
            raise app.InvalidCredentials
        if user.disabled:
            app.logger.info(f'User disabled: {user.id}')
            raise app.InvalidCredentials
        return user
    except JWTError as e: 
        print(f"DEBUG EXACT ERROR: {e}")
        app.logger.warning('Token is invalid or expired')
        raise app.InvalidCredentials
        
    except Exception:
        db.rollback()
        app.logger.exception('failed to get user')
        raise HTTPException(status_code=500, detail='Error getting user')


def get_current_active_user(
    current_user = Depends(get_current_user),
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



