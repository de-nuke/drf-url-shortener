from django.contrib import admin

from shortener.models import URL


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    search_fields = ("shortcut", "original")
    list_display = ("shortcut", "original", "shortened_url", "created", "last_accessed", "use_count")
