from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    USERNAME_FIELD = "username"

    DURATIONS = (
        (30, "30m"),
        (60, "1h"),
        (180, "3h"),
        (360, "6h"),
        (720, "12h"),
        (1440, "24h"),
        (2880, "48h"),
        (4320, "72h"),
        (10080, "7d"),
        (20160, "14d"),
        (525600, "30d"),
        (0, "∞"),
    )

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

    durations_available = ArrayField(
        models.PositiveIntegerField(choices=DURATIONS, blank=True, null=True),
        choices=DURATIONS,
        default=[_[0] for _ in DURATIONS[:4]]
    )
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
#
#     def get_concurrency_limit(self):
#         r = 1
#         now = datetime.now()
#         self.permissions.filter(
#             type__in=(
#                 Permission.TYPE_CONCURRENCY_LIMIT_5,
#                 Permission.TYPE_CONCURRENCY_LIMIT_10
#             ),
#             start__lt=now,
#             stop__lt=now
#         )
#
#
# class Permission(models.Model):
#
#     TYPE_CONCURRENCY_LIMIT_5 = 1
#     TYPE_CONCURRENCY_LIMIT_10 = 2
#     TYPES = (
#         (TYPE_CONCURRENCY_LIMIT_5, "Concurrency Limit: 5"),
#         (TYPE_CONCURRENCY_LIMIT_10, "Concurrency Limit: 10"),
#     )
#
#     type = models.PositiveIntegerField(choices=TYPES)
#     user = models.ForeignKey(User, related_name="permissions")
#     start = models.DateTimeField(auto_now_add=True)
#     stop = models.DateTimeField()
