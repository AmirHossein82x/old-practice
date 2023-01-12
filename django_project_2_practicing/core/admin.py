from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUser
# Register your models here.

@admin.register(User)
class UserAdmin(BaseUser):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", 'email', 'first_name', 'last_name'),
            },
        ),
    )
    search_fields = ['username']