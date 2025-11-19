from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate
from app.utils.hash import hash_password

router = APIRouter(prefix="/users", tags=["Users"])

# CREATE USER
@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pass = hash_password(user.password)

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        age=user.age,
        email=user.email,
        password=hashed_pass,
        role="Employee",
        department=None
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# GET ALL USERS
@router.get("/", response_model=list[UserRead])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# GET USER BY ID
@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: str, update_data: UserUpdate, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields if provided
    if update_data.first_name is not None:
        user.first_name = update_data.first_name

    if update_data.last_name is not None:
        user.last_name = update_data.last_name

    if update_data.age is not None:
        user.age = update_data.age

    if update_data.email is not None:
        # email must be unique
        email_exists = db.query(User).filter(User.email == update_data.email).first()
        if email_exists and email_exists.id != user.id:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = update_data.email

    if update_data.password is not None:
        user.password = hash_password(update_data.password)

    if update_data.role is not None:
        user.role = update_data.role

    if update_data.department is not None:
        user.department = update_data.department

    db.commit()
    db.refresh(user)

    return user

@router.delete("/{user_id}")
def delete_user(user_id:str, db: Session = Depends(get_db))
    
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)     # remove row from database
    db.commit()         # save changes
    db.refresh()
    

    return {"message": "User deleted successfully"}
    
