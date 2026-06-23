from fastapi import APIRouter,Depends,HTTPException
from app.db import get_db
from ..models import pool_members,pools,users,notifications
router= APIRouter(tags=['admin'])
from app import app
from ..security.OAuth2 import get_current_active_user
from sqlalchemy.orm import session
from uuid import UUID 
from ..schemas import users as schemaUsers
from ..policy.policy_engine import require_scope

@router.get('/users')
def get_users(db: session = Depends(get_db), current_user = Depends(require_scope('admin'))):
    user = db.query(users.User).all()
    return user