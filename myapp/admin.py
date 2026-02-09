from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Patient,
    ProfileIcon,
    Slider,
    Doctor,
    Medicine,
    MedicineSale,
    Department,
    User,
)

# ================= CUSTOM USER ADMIN =================
class UserAdmin(BaseUserAdmin):
    model = User
    ordering = ("email",)
    list_display = ("email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Information", {
            "fields": (
                "full_name",
                "phone",
                "address",
                "place",
                "profile_image",
            )
        }),
        ("Permissions", {
            "fields": (
                "role",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important Dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role"),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")


# ================= REGISTER MODELS =================
admin.site.register(User, UserAdmin)

admin.site.register(Patient)
admin.site.register(ProfileIcon)
admin.site.register(Slider)
admin.site.register(Doctor)
admin.site.register(Medicine)
admin.site.register(MedicineSale)
admin.site.register(Department)
