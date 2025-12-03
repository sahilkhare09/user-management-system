from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.import_service import import_users_from_excel
from app.core.security import get_current_user
from app.schemas.user_schema import ExcelImportResult

router = APIRouter(prefix="/api/v1/import", tags=["Excel Import"])


@router.post("/users", response_model=ExcelImportResult)
async def import_users(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Only superadmin or org-admin
    if current_user.role not in ["superadmin", "organisation_admin"]:
        raise HTTPException(403, "You are not allowed to import users")

    if not file.filename.endswith(".xlsx"):
        raise HTTPException(400, "Only .xlsx file is allowed")

    return import_users_from_excel(db, file, current_user)
