from fastapi import FastAPI, Request
from app.database.db import Base, engine

from app.routers.user_router import router as user_router
from app.routers.auth_router import router as auth_router
from app.routers.organisation_router import router as org_router
from app.routers.department_router import router as dept_router
from app.routers.log_router import router as log_router
from app.routers.import_router import router as import_router


app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(">>> HEADERS:", dict(request.headers))
    response = await call_next(request)
    return response


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(org_router)
app.include_router(dept_router)
app.include_router(log_router)
app.include_router(import_router)


@app.get("/")
def home():
    return {"message": "Database connected!"}
