from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    USERNAME_FIELD = "username"

    STATUS_ACTIVE = 1
    STATUS_DISABLED = 2
    STATUSES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_DISABLED, "Disabled"),
    )

    username = models.CharField(max_length=64, unique=True)
    is_staff = models.BooleanField(
        "Staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site."
    )
    is_active = models.BooleanField(
        "Active",
        default=True,
        help_text="Designates whether this user can log into the primary site."
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    status = models.PositiveIntegerField(
        verbose_name="Twitter Status",
        choices=STATUSES,
        default=STATUS_ACTIVE,
        help_text='A user is marked as "disabled" when the collector receives '
                  'a 401 from Twitter'
    )

    objects = UserManager()

    def __unicode__(self):
        return self.name

    def get_full_name(self):
        return self.get_username()

    def get_short_name(self):
        return self.get_username()

    def get_username(self):
        return self.username
