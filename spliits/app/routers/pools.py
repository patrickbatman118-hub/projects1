from fastapi import APIRouter, Depends
from sqlalchemy.orm import session
from .. import app,db
from ..models.pools import pool as models
from ..schemas.pools import pool as schemas
from ..security.OAuth2 import get_current_active_user


router = APIRouter()


@router.post('/createpool')
def create_pool(pool: schemas, db: session = Depends(db.get_db),current_user = Depends(get_current_active_user)):
    try:
        new_pool = models(**pool.model_dump())
        new_pool.host_id = current_user.id
        db.add(new_pool)
        db.commit()
        db.refresh(new_pool)
        return new_pool
    except Exception:
        app.logger.exception(f'Error creating pool: {pool}')
        db.rollback()
        raise app.HTTPException(status_code=500, detail={'Message': 'Error creating pool'})


@router.post('/deletepool')
def del_pool(db: session = Depends(db.get_db),current_user = Depends(get_current_active_user)):
    pool = db.query(models).filter(models.host.id == current_user.id).first()
    if not pool:
        app.logger.warning(f'No Pool Exists: {current_user.id}')
        raise app.NoPoolExist
    db.delete(pool)
    db.commit()
    return 'deleted'

