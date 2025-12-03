from tortoise import fields, models


class AdminUser(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(100, unique=True)
    password = fields.CharField(200)

    class Meta:
        table = "admin_users"

    def __str__(self):
        return self.username
