# app/routers/log_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.log import ActivityLog
from app.core.security import get_current_user, require_org_admin

router = APIRouter(prefix="/api/v1/logs", tags=["Logs"])


@router.get("/")
def get_logs(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(require_org_admin),  # 🔥 FIXED
):

    offset = (page - 1) * limit

    logs = (
        db.query(ActivityLog)
        .order_by(ActivityLog.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {"page": page, "limit": limit, "logs": logs}
