from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.audit_log import AuditLog


class AuditLogger:
    @staticmethod
    def log_action(
        db: Session,
        entity_name: str,
        entity_id: str,
        action: str,
        performed_by_id: Optional[int] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: str = "127.0.0.1"
    ) -> AuditLog:
        entry = AuditLog(
            entity_name=entity_name,
            entity_id=str(entity_id),
            action=action,
            performed_by_id=performed_by_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
