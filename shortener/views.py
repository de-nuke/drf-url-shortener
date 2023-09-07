from django.db.models import F
from django.db.models.functions import Now
from django.shortcuts import get_object_or_404
from django.views import generic
from rest_framework import mixins, viewsets

from shortener.models import URL
from shortener.serializers import URLSerializer


class CreateRetrieveURLViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Create shortcut by POST-ing original url or GET the URL details by shortcut."""

    authentication_classes: list[type] = []
    serializer_class = URLSerializer
    lookup_field = lookup_url_kwarg = "shortcut"
    queryset = URL.objects.all()


class ResolveURLView(generic.RedirectView):
    """Find original URL by shortcut and redirect to it. Update URL's usage data."""

    permanent = False

    def get_redirect_url(self, shortcut: str) -> str:
        url = get_object_or_404(URL, shortcut=shortcut)
        URL.objects.filter(id=url.id).update(last_accessed=Now(), use_count=F("use_count") + 1)
        return url.original
