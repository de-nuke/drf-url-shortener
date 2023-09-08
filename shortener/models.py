import urllib.parse

from django.conf import settings
from django.db import models
from django.urls import reverse

from shortener import constants


class URL(models.Model):
    """An entity representing shortened URL along with some metadata."""

    original = models.URLField("Original URL")
    shortcut = models.CharField("Shortcut", max_length=constants.MAX_SHORTCUT_LENGTH, db_index=True, unique=True)
    created = models.DateTimeField("Date of creation", auto_now_add=True)
    last_accessed = models.DateTimeField("Date of last access", null=True)
    use_count = models.PositiveIntegerField("Number of uses", default=0)

    @property
    def shortened_url(self) -> str:
        """Full shortened URL that user can visit to be redirected to the original URL."""
        path = reverse("resolve-url", args=(self.shortcut,))
        return urllib.parse.urljoin(settings.SITE_URL, path)

    def __str__(self) -> str:
        return f"{self.shortcut} ({self.original})"
