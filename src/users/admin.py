from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from allauth.account.models import EmailAddress

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "twitter", "status", "is_staff")
    list_filter = ("is_staff", "status")
    readonly_fields = ("password", "last_login", "username", "groups")

    def twitter(self, obj):
        return mark_safe(
            '<a href="https://twitter.com/{t}">{t}</a>'.format(t=obj.username))


admin.site.register(User, UserAdmin)

admin.site.unregister(EmailAddress)
admin.site.unregister(Group)
admin.site.unregister(Site)
