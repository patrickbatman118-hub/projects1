from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from app import schemas, models,db,app
from sqlalchemy.orm import session
from app.security.hash_password import hash_password
from app.security.authentication import create_access_token, create_refresh_token
from app.security.OAuth2 import get_current_active_user1
from fastapi.responses import RedirectResponse
from uuid import UUID
from ..models.users import User
from ..policy.policy_engine import require_scope
from app.utils.s3 import upload_to_s3,delete_from_s3
router = APIRouter(tags=['users'])

def build_scopes(user: User):
    scopes = ["user"]
    if user.is_admin:
        scopes.append("admin")
    return scopes

@router.post('/signup')
def signup(user: schemas.users.user,db: session = Depends(db.get_db)):
    try:
        get_user = (
            db.query(models.users.User)
            .filter(models.users.User.email == user.email)
            .first()
        )
        if not get_user:
            new_user = hash_password(user)
            db.add(new_user)
            db.flush()
            db.refresh(new_user)
            app.logger.info(f'User Created: {user.email}')
            scopes = build_scopes(new_user)
            access_token = create_access_token(data={"sub": str(new_user.user_id), "scopes": scopes})
            refresh_token = create_refresh_token(data={"sub": str(new_user.user_id)})
            db.commit()
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
def get_user(id: UUID, db: session = Depends(db.get_db), current_user=Depends(require_scope('user'))):
    user = (
        db.query(models.users.User)
        .filter(models.users.User.user_id == id, models.users.User.disabled == False)
        .first()
    )
    if not user:
        app.logger.warning(f'No User Exists: {id}')
        raise app.NoUserExists
    return user

@router.delete('/deleteuser')
def del_user( db: session = Depends(db.get_db), current_user = Depends(get_current_active_user1)):
    try:        
        get_user = (
            db.query(models.users.User)
            .filter(models.users.User.user_id == current_user.user_id)
            .first()
        )
        if not get_user:
            app.logger.warning(f'No User Exists: {current_user.user_id}')
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
        app.logger.exception(f'Error deleting user: {current_user.user_id}')
        db.rollback()
        raise HTTPException(status_code=500, detail={'Message': 'Error deleting user'})
    
@router.put('/updateuser')
def update_user(user: schemas.users.userupdate, db: session = Depends(db.get_db), current_user = Depends(get_current_active_user1)):
    try:
        get_user = (
            db.query(models.users.User)
            .filter(models.users.User.user_id == current_user.user_id)
            .first()
        )
        if not get_user:
            app.logger.warning(f'No User Exists: {current_user.user_id}')
            raise app.NoUserExists
        get_user.name = user.name
        get_user.pfp = user.pfp
        db.commit()
        db.refresh(get_user)
        return get_user
    except app.NoUserExists:
        raise
    except Exception:
        app.logger.exception(f'Error updating user: {current_user.user_id}')
        db.rollback()
        raise HTTPException(status_code=500, detail={'Message': 'Error updating user'})


@router.get('/me',response_model=schemas.users.UserResponse)
def get_user(db: session = Depends(db.get_db), current_user = Depends(get_current_active_user1)):
    user = (
        db.query(models.users.User)
        .filter(models.users.User.user_id == current_user.user_id, models.users.User.disabled == False)
        .first()
    )
    if not user:
        app.logger.warning(f'No User Exists: {current_user.user_id}')
        raise app.NoUserExists
    return user

@router.post('/uploadpfp')
async def upload_pfp(file: UploadFile = File(...), db: session = Depends(db.get_db), current_user = Depends(get_current_active_user1)):
    try:
        get_user = (
            db.query(models.users.User)
            .filter(models.users.User.user_id == current_user.user_id)
            .first()
        )
        if not get_user:
            app.logger.warning(f'No User Exists: {current_user.user_id}')
            raise app.NoUserExists
        
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail={'Message': 'Invalid file type. Only JPEG, PNG are allowed.'})
        if get_user.pfp is not None:
            delete_from_s3(get_user.pfp)
        url = await upload_to_s3(file, str(get_user.user_id))
        get_user.pfp = url
        db.commit()
        db.refresh(get_user)
        return {"message": "Profile picture uploaded successfully.", "pfp_url": get_user.pfp}
    except app.NoUserExists:
        raise
    except Exception:
        app.logger.exception(f'Error uploading profile picture for user: {current_user.user_id}')
        db.rollback()
        raise HTTPException(status_code=500, detail={'Message': 'Error uploading profile picture'})

