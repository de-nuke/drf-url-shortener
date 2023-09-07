import pytest
from django.urls import path

from shortener.factories import URLFactory
from tests.utils import mock_url_patterns


@pytest.mark.parametrize(
    "url_pattern, site_url, shortcut, expected_full_url",
    [
        ("<slug:shortcut>/", "http://testserver", "tdEaR", "http://testserver/tdEaR/"),
        ("resolve/<slug:shortcut>/", "https://localhost/", "8iut81", "https://localhost/resolve/8iut81/"),
    ],
)
@pytest.mark.django_db
def test_url_shortened_url(url_pattern, site_url, shortcut, expected_full_url, settings):
    """Test `shortener.models.URL.shortened_url`. Check that the property correctly builds absolute URL."""

    url_patterns = [path(url_pattern, lambda _: _, name="resolve-url")]
    with mock_url_patterns(url_patterns):
        settings.SITE_URL = site_url

        url = URLFactory(shortcut=shortcut)
        assert url.shortened_url == expected_full_url


@pytest.mark.django_db
def test_url_str():
    """Test `shortener.models.URL.__str__`. Check that it returns correct string representation of URL object."""
    url = URLFactory(shortcut="test1", original="https://www.google.com")
    assert str(url) == "test1 (https://www.google.com)"
