from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from redis.asyncio import Redis

# IMPORTANT: real admin routes are here
from fastapi_admin.routes import router as admin_router


async def init_admin(app):

    redis = Redis(host="localhost", port=6379, decode_responses=True)

    provider = UsernamePasswordProvider(
        admin_model=None,  # your version does NOT use this to build CRUD
    )

    await admin_app.configure(
        redis=redis,
        logo_url="https://via.placeholder.com/150",
        providers=[provider],
        admin_path="/admin",
        default_locale="en_US",
        language_switch=True,
    )

    # ✔ Mount actual admin API router
    app.include_router(admin_router, prefix="/admin")
