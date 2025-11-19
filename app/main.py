from fastapi import FastAPI
from app.database.db import Base, engine
from app.routers.user_router import router as user_router

from app.models.user import User
from app.models.organisation import Organisation

app = FastAPI()

# Register your user router
app.include_router(user_router)   # <-- VERY IMPORTANT

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Database connected!"}
