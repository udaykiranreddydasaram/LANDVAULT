from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db, require_roles
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User

router = APIRouter()


@router.get("/logs")
def list_audit_logs(
    action_filter: Optional[str] = None,
    entity_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    query = db.query(AuditLog)
    if action_filter:
        query = query.filter(AuditLog.action == action_filter)
    if entity_filter:
        query = query.filter(AuditLog.entity_name == entity_filter)

    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

    result = []
    for l in logs:
        actor = db.query(User).filter(User.id == l.performed_by_id).first() if l.performed_by_id else None
        result.append({
            "id": l.id,
            "entity_name": l.entity_name,
            "entity_id": l.entity_id,
            "action": l.action,
            "performed_by": actor.full_name if actor else "System Automated Worker",
            "performed_by_role": actor.role if actor else "system",
            "old_values": l.old_values,
            "new_values": l.new_values,
            "ip_address": l.ip_address,
            "timestamp": str(l.timestamp)
        })
    return result
