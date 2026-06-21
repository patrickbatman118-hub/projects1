from fastapi import APIRouter, Depends, HTTPException, Response
from app import schemas, models,db,app
from sqlalchemy.orm import session
from app.security.hash_password import hash_password
from app.security.authentication import create_access_token, create_refresh_token
from app.security.OAuth2 import get_current_active_user
from fastapi.responses import RedirectResponse


router = APIRouter(tags=['users'])

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

@router.get('/uers',response_model=list[schemas.users.UserResponse])
def get_users(db: session = Depends(db.get_db)):
    users = db.query(models.users.User).filter(models.users.User.disabled == False).all()
    return users    

@router.get('/user/{id}', response_model=schemas.users.UserResponse)
def get_user(id: int, db: session = Depends(db.get_db)):
    user = db.query(models.users.User).filter(models.users.User.id == id, models.users.User.disabled == False).first()
    if not user:
        app.logger.warning(f'No User Exists: {id}')
        raise app.NoUserExists
    return user

@router.delete('/deleteuser')
def del_user( db: session = Depends(db.get_db), current_user = Depends(get_current_active_user)):
    try:        
        get_user = db.query(models.users.User).filter(models.users.User.id == current_user.id).first()
        if not get_user:
            app.logger.warning(f'No User Exists: {current_user.id}')
            raise app.NoUserExists
        db.delete(get_user)
        db.commit()
        res = RedirectResponse(url='/login',status_code=303)
        res.delete_cookie(key='access_token')
        res.delete_cookie(key='refresh_token')
        return res
    except app.NoUserExists:
        raise
    except Exception:
        app.logger.exception(f'Error deleting user: {current_user.id}')
        db.rollback()
        raise HTTPException(status_code=500, detail={'Message': 'Error deleting user'})
    
@router.put('/updateuser')
def update_user(user: schemas.users.userupdate, db: session = Depends(db.get_db), current_user = Depends(get_current_active_user)):
    try:
        get_user = db.query(models.users.User).filter(models.users.User.id == current_user.id).first()
        if not get_user:
            app.logger.warning(f'No User Exists: {current_user.id}')
            raise app.NoUserExists
        get_user.name = user.name
        get_user.pfp = user.pfp
        db.commit()
        db.refresh(get_user)
        return get_user
    except app.NoUserExists:
        raise
    except Exception:
        app.logger.exception(f'Error updating user: {current_user.id}')
        db.rollback()
        raise HTTPException(status_code=500, detail={'Message': 'Error updating user'})
    

