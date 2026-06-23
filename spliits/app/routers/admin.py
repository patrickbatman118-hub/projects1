from fastapi import APIRouter,Depends,HTTPException
from app.db import get_db
from ..models import pool_members,pools,users,notifications
router= APIRouter(tags=['admin'])
from app import app
from ..security.OAuth2 import get_current_active_user
from sqlalchemy.orm import session
from uuid import UUID 
from ..utils.enum import request_status

@router.get('/allusers')
def get_users():
    pass