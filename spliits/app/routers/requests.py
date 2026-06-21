from fastapi import APIRouter,Depends,HTTPException
from app.db import get_db
from ..models import pool_members,pools,users,notifications
router= APIRouter(tags=['requests'])
from app import app
from ..security.OAuth2 import get_current_active_user
from sqlalchemy.orm import session
from uuid import UUID 
from ..utils.enum import request_status

@router.post('/sendrequest/{id}')
def request_pool(id: UUID,db: session = Depends(get_db), current_user = Depends(get_current_active_user)):
    try:
        get_pool = db.query(pools.pool).filter(pools.pool.pool_id == id).first()
        try_user = db.query(pool_members).filter(pool_members.user_id == current_user.user_id).first()
        if not get_pool:
            app.logger.warning(f'No pool exists: {UUID}')
            app.No_Pool_Found
        if get_pool.host_id == current_user.user_id:
            app.logger.warning(f'multiple request')
            app.already_in_pool_exception_handler
        if try_user:
            app.logger.warning(f'multiple requests')
            app.already_in_pool_exception_handler
        new_member = pool_members()
        new_member.pool_id = get_pool.pool_id
        new_member.user_id = current_user.user_id
        new_member.host_id = get_pool.host_id
        notification = notifications(
        sender_id = current_user.user_id,
        receiver_id = get_pool.host_id,
        content = (f'New Request from {current_user.name}') 
        )
        db.add(notification)
        db.add(new_member)
        db.commit()
        app.logger.info(f'sent request')
        return('sent request')
    except HTTPException:
        raise
    except Exception:
        app.logger.exception(f'Error sending Request')
        db.rollback()
        raise HTTPException(status_code=500, detail='Error Sending Request')
    
@router.get('/getrequest')
def getrequests(db: session = Depends(get_db), current_user = Depends(get_current_active_user)):
    requests = db.query(pool_members).filter(pool_members.host_id == current_user.user_id, pool_members.status == 'requested').outerjoin(users.User, users.User.user_id == pool_members.host_id).all()
    return requests

@router.post('/acceptrequest/{id}')
def approverequest(id: UUID,approval:request_status,db: session = Depends(get_db), current_user = Depends(get_current_active_user) ):
    try:    
        get_request = db.query(pool_members).filter(pool_members.member_id == id, pool_members.host_id == current_user.user_id).first()
        if not get_request:
            app.logger.warning(f'No such request found: {pool_members.member_id}')
            raise HTTPException(status_code=404, detail=(f'No request found'))
        if get_request.status in {'accepted','rejected'}:
            app.logger.warning(f'trying to accept/reject user whose already completed')
            raise HTTPException(status_code=409, detail=(f'Conflict'))
        get_request.status = approval.value
        db.add(get_request)
        db.flush()
        notification = notifications(
            sender_id = current_user.user_id,
            receiver_id = get_request.user_id,
            content = (f'Request Accepted: {get_request.pool_id}')
        )
        db.add(notification)
        db.commit()
        return
    except HTTPException:
        raise
    except Exception:
        app.logger.exception('Error rejecting/accepting request')
        db.rollback()
        raise HTTPException(status_code=500, detail=(f'An Error Occured'))
