from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import session
from .. import app,db
from ..models.pools import pool as models
from ..schemas import pools
from ..security.OAuth2 import get_current_active_user1, get_current_user
from sqlalchemy import func
from uuid import UUID
from ..models.pool_members import pool_members
from ..policy.policies import policy_engine
from ..policy.policy_engine import require_scope
router = APIRouter(tags=['pools'])


@router.post('/createpool')
def create_pool(pool: pools.pool, db: session = Depends(db.get_db),current_user = Depends(require_scope('user'))):
    try:
        count = db.query(func.count(models.pool_id)).filter(models.host_id == current_user.user_id,func.extract('day', func.age(func.now(), models.created_at)) <= 30).scalar()
        countday = db.query(func.count(models.pool_id)).filter(models.host_id == current_user.user_id,func.extract('day', func.age(func.now(), models.created_at)) <= 1).scalar()
        if count > 3 :
            app.logger.warning(f'Repeated pool creations from user: {current_user.user_id}')
            raise HTTPException(status_code=429, detail='Too many pool creation requests in a month')
        if countday > 3 :
            app.logger.warning(f'Repeated pool creations from user: {current_user.user_id}')
            raise HTTPException(status_code=429, detail='Too many pool creation requests in a day')
        new_pool = models(**pool.model_dump())
        new_pool.host_id = current_user.user_id
        db.add(new_pool)
        db.flush()
        member = pool_members(
            user_id=current_user.user_id,
            pool_id=new_pool.pool_id,
            host_id=current_user.user_id,
            status='accepted',
            role='host'
        )
        db.add(member)
        db.commit() 
        db.refresh(new_pool)
        return new_pool
    except HTTPException:
        raise
    except Exception:
        app.logger.exception(f'Error creating pool: {pool}')
        db.rollback()
        raise app.HTTPException(status_code=500, detail={'Message': 'Error creating pool'})


@router.delete('/deletepool/{id}')
def del_pool(id: UUID,db: session = Depends(db.get_db),current_user = Depends(require_scope('user'))):#####
    try:      
        pool = db.query(models).filter(models.host_id == current_user.user_id, models.pool_id == id).first()
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
def update_pool(id:UUID,pool: pools.updatepool, db: session = Depends(db.get_db), current_user = Depends(get_current_user)):
    try:    
        get_pool = db.query(models).filter(models.pool_id == id).first()
        if not get_pool:
            app.logger.warning(f'No Pool Exists: {id}')
            raise app.NoPoolExist
        allowed, reason = policy_engine.check('update','pool',current_user, get_pool)
        if not allowed:
            app.logger.warning(f"denied actor={current_user.user_id} action=update pool:{get_pool.pool_id} reason={reason}")
            raise app.ForbiddenUser
        update_data = pool.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(get_pool, key, value)
        db.commit()
        db.refresh(get_pool)
        return get_pool
    except (app.ForbiddenUser,app.NoPoolExist):
        raise
    except Exception:
        app.logger.exception(f'Error updating pool: {pool}')
        db.rollback()
        raise HTTPException(status_code=500, detail={'Message': 'Error updating pool'})
    
@router.get('/pools', response_model=list[pools.PoolResponse])
def get_pools(db: session = Depends(db.get_db)):
    pools = db.query(models).join(pool_members,pool_members.pool_id == models.pool_id).filter(models.is_active == True).all()
    return pools

@router.get('/pool/mypools', response_model=list[pools.PoolResponse])
def get_pool( db: session = Depends(db.get_db), current_user = Depends(require_scope('user'))):
    pools = db.query(models).filter( models.is_active == True,models.host_id == current_user.id).all()
    return pools


             


    

    