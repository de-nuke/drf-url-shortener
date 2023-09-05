from rest_framework import exceptions, serializers

from shortener import shortcuts
from shortener.models import URL


class URLSerializer(serializers.ModelSerializer):
    """Serializer for `shortener.models.URL`."""

    url = serializers.URLField(source="original")

    def validate(self, attrs):
        try:
            shortcut = shortcuts.get_shortcut()
        except shortcuts.GenerationError as e:
            raise exceptions.ValidationError(str(e)) from e
        attrs["shortcut"] = shortcut
        return attrs

    class Meta:
        model = URL
        read_only_fields = ["shortcut", "created", "last_accessed", "use_count", "shortened_url"]
        fields = ["url", *read_only_fields]
