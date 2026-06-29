from sqlalchemy.orm import session
from .models.audit_log import AuditLog
import app

RESOURCE_ID_FIELD = {
    "pool": "pool_id",
    "join_request": "request_id",
    "membership": "membership_id",
}

def get_resource_id(resource_type: str, resource) -> str | None:
    if resource is None:
        return None
    field = RESOURCE_ID_FIELD.get(resource_type)
    return str(getattr(resource, field, None)) if field else None

def log_decision(db: session, actor, action: str, resource_type: str, resource_id, decision: str, reason: str, jti: str = None):
    try:
        entry = AuditLog(
            actor_id=actor.user_id if actor else None,
            jti=jti,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            decision=decision,
            reason=reason,
        )
        db.add(entry)
    except Exception:
        app.logger.exception(f'Failed to write audit log: actor={actor.user_id if actor else None} action={action}')
        db.rollback()