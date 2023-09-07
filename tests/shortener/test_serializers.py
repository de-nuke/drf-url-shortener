from unittest import mock

import pytest
from rest_framework.exceptions import APIException

import shortener.shortcuts
from shortener.models import URL
from shortener.serializers import URLSerializer


@pytest.mark.django_db
def test_url_serializer_creates_url(mocker):
    """Test `shortener.serializers.URLSerializer`. Check that it creates URL instance with generated shortcut."""
    data = {"url": "https://example.com/"}
    serializer = URLSerializer(data=data)
    serializer.is_valid()

    get_shortcut_spy = mocker.spy(shortener.shortcuts, "get_shortcut")
    obj = serializer.save()

    get_shortcut_spy.assert_called()
    assert obj.shortcut == get_shortcut_spy.spy_return


@pytest.mark.django_db
def test_url_serializer_generation_error():
    """Test `shortener.serializers.URLSerializer`.

    Check that object is not created if there was a shortcut generation error.
    """
    data = {"url": "https://example.com/"}
    serializer = URLSerializer(data=data)
    serializer.is_valid()

    with mock.patch("shortener.shortcuts.get_shortcut", side_effect=shortener.shortcuts.GenerationError("test")):
        with pytest.raises(APIException) as exc_info:
            serializer.save()
    assert URL.objects.count() == 0
    assert str(exc_info.value) == "test"
