from datetime import datetime
from unittest import mock

import freezegun
import pytest
from django.urls import reverse

from shortener.factories import URLFactory
from shortener.models import URL
from shortener.shortcuts import GenerationError


@pytest.mark.django_db
def test_post_url(client):
    """Test that URL is created when valid data is posted."""
    response = client.post(reverse("url-list"), {"url": "https://example.com"})
    assert response.status_code == 201
    assert URL.objects.count() == 1
    assert URL.objects.first().original == "https://example.com"


@pytest.mark.django_db
def test_post_invalid_url(client):
    """Test that URL is not created if url is not valid and that error is returned."""
    response = client.post(reverse("url-list"), {"url": "invalid_url"})
    assert response.status_code == 400
    assert response.json() == {"url": ["Enter a valid URL."]}
    assert URL.objects.count() == 0


def test_post_generation_error(client):
    """Test that nice error is returned when there was shortcut generation error."""
    with mock.patch("shortener.shortcuts.get_shortcut", side_effect=GenerationError("Generation error test msg")):
        response = client.post(reverse("url-list"), {"url": "https://example.com"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Generation error test msg"}


@pytest.mark.django_db
def test_get_url_details(client, settings):
    """Test that URL details can be retrieved by shortcut"""
    test_shortcut = "testtest"
    test_original = "https://testserver/"
    settings.SITE_URL = "http://localhost:8000/"

    with freezegun.freeze_time("2023-09-06T11:19:05.496782Z"):
        URLFactory(shortcut=test_shortcut, original=test_original)

    response = client.get(reverse("url-detail", args=(test_shortcut,)))
    assert response.status_code == 200
    assert response.json() == {
        "url": test_original,
        "shortcut": test_shortcut,
        "created": "2023-09-06T11:19:05.496782Z",
        "last_accessed": None,
        "use_count": 0,
        "shortened_url": "http://localhost:8000/" + test_shortcut + "/",
    }


@pytest.mark.django_db
def test_get_url_not_found(client):
    """Test that 404 is returned if the shortcut is wrong."""
    test_shortcut = "testtest"
    url = URLFactory(shortcut=test_shortcut)
    response = client.get(reverse("url-detail", args=(str(url.id),)))
    assert response.status_code == 404


@pytest.mark.django_db
def test_redirect(client):
    """Test that resolving shortcut into original URL works."""
    test_shortcut = "testtest"
    test_original = "https://testserver/"
    URLFactory(shortcut=test_shortcut, original=test_original)

    response = client.get(reverse("resolve-url", args=(test_shortcut,)), follow=False)
    assert response.status_code == 302
    assert response.url == test_original


@pytest.mark.django_db
def test_redirect_invalid_shortcut(client):
    """Test that 404 is raised if non-existing shortcut is attempted to be resolved."""
    test_shortcut = "testtest"
    URLFactory(shortcut=test_shortcut)

    response = client.get(reverse("resolve-url", args=("invalid",)), follow=False)
    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize("n_uses", [0, 1, 5])
def test_redirect_update_url_usage(client, n_uses):
    """Test that `use_count` and `last_accessed` attributes of URL are updated when its resolved."""
    test_shortcut = "testtest"

    url = URLFactory(shortcut=test_shortcut)
    assert url.last_accessed is None
    assert url.use_count == 0

    for _ in range(n_uses):
        response = client.get(reverse("resolve-url", args=(test_shortcut,)), follow=False)
        assert response.status_code == 302

    url.refresh_from_db()
    if n_uses > 1:
        assert url.last_accessed is not None
        assert isinstance(url.last_accessed, datetime)
    assert url.use_count == n_uses
