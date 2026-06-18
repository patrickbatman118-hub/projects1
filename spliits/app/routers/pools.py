from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import session
from .. import app,db
from ..models.pools import pool as models
from ..schemas import pools
from ..security.OAuth2 import get_current_active_user


router = APIRouter()


@router.post('/createpool')
def create_pool(pool: pools.pool, db: session = Depends(db.get_db),current_user = Depends(get_current_active_user)):
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


@router.delete('/deletepool/{id}')
def del_pool(id: int,db: session = Depends(db.get_db),current_user = Depends(get_current_active_user)):
    try:      
        pool = db.query(models).filter(models.host_id == current_user.id, models.id == id).first()
        if not pool:
            app.logger.warning(f'No Pool Exists: {id}')
            raise app.NoPoolExist
        db.delete(pool)
        db.commit()
        return 'deleted'
    except app.NoPoolExist:
        raise
    except Exception:
        app.logger.exception(f'Error deleting pool: {pool}')
        db.rollback()
        raise HTTPException(status_code=500, detail={'Message': 'Error deleting pool'})


@router.put('/updatepool/{id}')
def update_pool(id:int,pool: pools.updatepool, db: session = Depends(db.get_db), current_user = Depends(get_current_active_user)):
    try:    
        get_pool = db.query(models).filter(models.host_id == current_user.id, models.id == id).first()
        if not pool:
            app.logger.warning(f'No Pool Exists: {id}')
            raise app.NoPoolExist
        get_pool.title = pool.title
        get_pool.description = pool.description
        get_pool.total_cost = pool.total_cost
        get_pool.max_members = pool.max_members
        db.commit()
        db.refresh(get_pool)
        return get_pool
    except app.NoPoolExist:
        raise
    except Exception:
        app.logger.exception(f'Error updating pool: {pool}')
        db.rollback()
        raise HTTPException(status_code=500, detail={'Message': 'Error updating pool'})
    

    