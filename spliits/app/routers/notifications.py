from fastapi import APIRouter,Depends,HTTPException
from app.db import get_db
from ..models import pool_members,pools,users,notifications
router= APIRouter(tags=['notifications'])
from app import app
from ..security.OAuth2 import get_current_user,get_current_active_user1
from sqlalchemy.orm import session
from uuid import UUID 
from ..schemas.micallenious import NotificationResponseSchema
from ..policy.policy_engine import require_scope

@router.get('/notifications/read-all', response_model=NotificationResponseSchema)
def read_all_notifications(db: session = Depends(get_db), current_user = Depends(require_scope('user'))):
    notification = db.query(notifications).filter(
        notifications.receiver_id == current_user.user_id
    ).order_by(notifications.created_at.desc()).limit(30).all()
    if not notification:
        app.logger.warning('No notifications')
        HTTPException(status_code=404, detail=('No notifications'))
    unread_count = db.query(notifications).filter(
        notifications.receiver_id == current_user.user_id,
        notifications.is_read == False
    ).count()
    if not unread_count:
        app.logger.warning('No notifications')
        HTTPException(status_code=404, detail=('No notifications'))
    app.logger.info(f'Fetched notifications')
    return {
        "unread_count": unread_count,
        "notifications": notification
    } 