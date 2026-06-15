from fastapi import APIRouter, Depends, HTTPException
from app import schemas, models,db,app
from sqlalchemy.orm import session
import bcrypt

router = APIRouter()

@router.post('/signup')
def signup(user: schemas.user,db: session = Depends(db.get_db)):
    try:
        get_user = db.query(models.User).filter(models.User.email == user.email).first()
        if not get_user:
            hashed_password = bcrypt.hashpw(user.password.encode(),bcrypt.gensalt()).decode()
            user_data = user.model_dump()
            user_data['password'] = hashed_password
            user_data.pop('confirm_password')
            new_user = models.User(**user_data)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        else:
            raise app.EmailAlreadyExists
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(Status_code=500, detail={'Message': 'Error creating user'})