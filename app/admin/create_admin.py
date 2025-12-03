from tortoise import Tortoise, run_async
from app.admin.models import AdminUser


async def create_admin():
    await Tortoise.init(
        db_url="sqlite://admin.sqlite3",
        modules={"models": ["app.admin.models"]},
    )
    await Tortoise.generate_schemas()

    await AdminUser.create(username="admin", password="admin123", is_superuser=True)

    print("⭐ Admin user created successfully!")


if __name__ == "__main__":
    run_async(create_admin())
