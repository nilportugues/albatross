from django.contrib import admin

from .models import Archive, Event


class ArchiveAdmin(admin.ModelAdmin):
    list_display = (
        "query", "user", "started", "stopped", "is_running", "allow_search",
        "status", "total"
    )
    list_filter = ("user", "started", "is_running", "allow_search", "status")
    readonly_fields = (
        "query", "user", "started", "is_running", "total", "cloud",
        "statistics", "images", "cloud_generated", "statistics_generated",
        "map_generated", "search_generated", "size", "last_distilled"
    )
    save_on_top = True

admin.site.register(Archive, ArchiveAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ("label", "archive", "time")
    list_filter = ("archive",)

admin.site.register(Event, EventAdmin)
