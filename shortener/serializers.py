from rest_framework import serializers
from rest_framework.exceptions import APIException

from shortener import shortcuts
from shortener.models import URL


class URLSerializer(serializers.ModelSerializer):
    """Serializer for `shortener.models.URL`."""

    url = serializers.URLField(source="original")

    def create(self, validated_data):
        """Generate "shortcut" before creating the URL instance."""
        try:
            validated_data["shortcut"] = shortcuts.get_shortcut()
        except shortcuts.GenerationError as e:
            raise APIException(str(e))
        return super().create(validated_data)

    class Meta:
        model = URL
        read_only_fields = ["shortcut", "created", "last_accessed", "use_count", "shortened_url"]
        fields = ["url", *read_only_fields]
