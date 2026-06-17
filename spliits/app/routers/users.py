from fastapi import APIRouter, Depends, HTTPException
from app import schemas, models,db,app
from sqlalchemy.orm import session
from app.security.hash_password import hash_password
from app.security.authentication import create_access_token, create_refresh_token


router = APIRouter()

@router.post('/signup')
def signup(user: schemas.users.user,db: session = Depends(db.get_db)):
    try:
        get_user = db.query(models.users.User).filter(models.users.User.email == user.email).first()
        if not get_user:
            new_user = hash_password(user)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            app.logger.info(f'User Created: {user.email}')
            access_token = create_access_token(data={"sub": user.id})
            refresh_token = create_refresh_token(data={"sub": user.id})
            return {'acces_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}
        else:
            app.logger.info(f'User Already Exists: {user.email}')
            raise app.EmailAlreadyExists
    except (HTTPException,app.EmailAlreadyExists):
        raise
    except Exception:
        app.logger.exception(f'Error creating user: {user.email}')
        db.rollback()
        raise HTTPException(status_code=500, detail={'Message': 'Error creating user'})
    

@router.get('/user/{id}', response_model=schemas.users.UserResponse)
def get_user(id: int, db: session = Depends(db.get_db)):
    user = db.query(models.users.User).filter(models.users.User.id == id).first()
    if not user:
        app.logger.warning(f'No User Exists: {id}')
        raise app.NoUserExists
    return user