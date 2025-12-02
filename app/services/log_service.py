from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from app.models.log import ActivityLog


# -------------------------------------------------------
# CREATE LOG ENTRY
# -------------------------------------------------------
def create_log(db: Session, user_id: UUID | None, action: str):
    try:
        log = ActivityLog(
            user_id=user_id,
            action=action
        )

        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    except Exception as e:
        db.rollback()
        # Avoid crashing API if log fails
        raise HTTPException(
            status_code=500,
            detail=f"Error creating activity log: {str(e)}"
        )
