from fastapi import APIRouter
from app.db import get_db
from models import pool_members,pools,users,notifications
router= APIRouter()


@router.post('request')
def request_pool: