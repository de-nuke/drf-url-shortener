from rest_framework import mixins, viewsets

from shortener.models import URL
from shortener.serializers import URLSerializer


class CreateRetrieveURLViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes: list[type] = []
    serializer_class = URLSerializer
    lookup_field = lookup_url_kwarg = "shortcut"
    queryset = URL.objects.all()
