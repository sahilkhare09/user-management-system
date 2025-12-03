from fastapi_admin.resources import ModelResource
from .models import AdminUser


class AdminUserResource(ModelResource):
    label = "Admin Users"
    model = AdminUser
    search_fields = ["username"]
    fields = ["id", "username", "password", "is_superuser"]
