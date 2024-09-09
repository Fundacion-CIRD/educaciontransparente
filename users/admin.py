from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from core.models import InstitutionUser
from users.models import User
from users.tasks import send_invite

admin.site.unregister(Group)


class InstitutionUserInline(TabularInline):
    model = InstitutionUser
    fields = ("institution", "is_manager")
    extra = 1
    min_num = 0
    autocomplete_fields = ("institution",)


@admin.action(description="Invitar usuarios seleccionados")
def invite_users(modeladmin, request, queryset):
    for user in queryset:
        send_invite(user)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ("email", "first_name", "last_name", "is_active")
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    ordering = ("email",)
    inlines = [InstitutionUserInline]
    readonly_fields = ("last_login", "date_joined")
    actions = [invite_users]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(institutions__in=request.user.institutions.all())

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None,
                    {
                        "classes": ("wide",),
                        "fields": (
                            "email",
                            "first_name",
                            "last_name",
                            "password1",
                            "password2",
                        ),
                    },
                ),
            )
        fieldsets = [
            (
                None,
                {
                    "fields": (
                        "email",
                        "password",
                        (
                            "first_name",
                            "last_name",
                        ),
                    )
                },
            ),
        ]
        if request.user.is_superuser:
            fieldsets.append(
                (
                    "Permisos",
                    {
                        "fields": (
                            "is_active",
                            "is_staff",
                            "is_superuser",
                        ),
                    },
                ),
            )
        return fieldsets
