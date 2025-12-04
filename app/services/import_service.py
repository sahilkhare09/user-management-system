import pandas as pd
from typing import List, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.organisation import Organisation
from app.models.department import Department
from app.utils.hash import hash_password

# REQUIRED_COLUMNS MUST be defined
REQUIRED_COLUMNS = [
    "first_name",
    "last_name",
    "age",
    "email",
    "password",
    "organisation_id",
    "department_id",
    "role",
]


def import_users_from_excel(db: Session, file, current_user):
    # read excel
    df = pd.read_excel(file.file)

    # sanitize: convert NaN to None and string "null"/"NULL" to None
    df = df.where(pd.notnull(df), None)
    df = df.replace({"null": None, "NULL": None})

    # ensure columns exist
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            # Use HTTPException so caller receives 400
            raise HTTPException(status_code=400, detail=f"Missing column: {col}")

    success_count = 0
    errors: List[Any] = []

    for index, row in df.iterrows():
        try:
            # --- Validate Organisation ---
            org = None
            if row["organisation_id"]:
                org = (
                    db.query(Organisation)
                    .filter(Organisation.id == row["organisation_id"])
                    .first()
                )
                if not org:
                    raise Exception("Invalid organisation_id")

                # Org admin cannot import for other orgs
                if current_user.role == "organisation_admin":
                    if current_user.organisation_id != org.id:
                        raise Exception("Cannot import for another organisation")

            # --- Validate Department ---
            dept = None
            if row["department_id"]:
                dept = (
                    db.query(Department)
                    .filter(Department.id == row["department_id"])
                    .first()
                )
                if not dept:
                    raise Exception("Invalid department_id")

                if org and dept.organisation_id != org.id:
                    raise Exception("Department does not belong to organisation")

            # --- Check duplicates ---
            existing = db.query(User).filter(User.email == row["email"]).first()
            if existing:
                raise Exception("Email already exists")

            # --- Create user ---
            user = User(
                first_name=row["first_name"],
                last_name=row["last_name"],
                age=int(row["age"]) if row["age"] is not None else None,
                email=row["email"],
                password=hash_password(row["password"]),
                role=row["role"],
                organisation_id=row["organisation_id"],
                department_id=row["department_id"],
            )

            db.add(user)
            db.commit()
            success_count += 1

        except Exception as e:
            # make sure values are JSON-serializable (native python types)
            errors.append(
                {"row": int(index) + 2, "error": str(e)}
            )
            db.rollback()

    # return native-Python types only
    return {
        "success_count": int(success_count),
        "failed_count": int(len(errors)),
        "errors": errors,
    }
