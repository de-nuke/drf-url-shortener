from datetime import datetime
from unittest import mock

import freezegun
import pytest
from django.urls import reverse

from shortener.factories import URLFactory
from shortener.models import URL
from shortener.shortcuts import GenerationError

URL_LIST_VIEW_NAME = "url-list"
URL_DETAIL_VIEW_NAME = "url-detail"
RESOLVE_URL_VIEW_NAME = "resolve-url"


@pytest.mark.django_db
def test_post_url(client, original_url):
    """Test that URL is created when valid data is posted."""
    response = client.post(reverse(URL_LIST_VIEW_NAME), {"url": original_url})
    assert response.status_code == 201
    assert URL.objects.count() == 1
    assert URL.objects.first().original == original_url


@pytest.mark.django_db
def test_post_invalid_url(client):
    """Test that URL is not created if url is not valid and that error is returned."""
    response = client.post(reverse(URL_LIST_VIEW_NAME), {"url": "invalid_url"})
    assert response.status_code == 400
    assert response.json() == {"url": ["Enter a valid URL."]}
    assert URL.objects.count() == 0


def test_post_generation_error(client, original_url):
    """Test that nice error is returned when there was shortcut generation error."""
    with mock.patch("shortener.shortcuts.get_shortcut", side_effect=GenerationError("Generation error test msg")):
        response = client.post(reverse(URL_LIST_VIEW_NAME), {"url": original_url})

    assert response.status_code == 500
    assert response.json() == {"detail": "Generation error test msg"}


@pytest.mark.django_db
def test_get_url_details(client, settings, shortcut, original_url):
    """Test that URL details can be retrieved by shortcut"""
    settings.SITE_URL = "http://localhost:8000/"

    with freezegun.freeze_time("2023-09-06T11:19:05.496782Z"):
        URLFactory(shortcut=shortcut, original=original_url)

    response = client.get(reverse(URL_DETAIL_VIEW_NAME, args=(shortcut,)))
    assert response.status_code == 200
    assert response.json() == {
        "url": original_url,
        "shortcut": shortcut,
        "created": "2023-09-06T11:19:05.496782Z",
        "last_accessed": None,
        "use_count": 0,
        "shortened_url": settings.SITE_URL + shortcut + "/",
    }


@pytest.mark.django_db
def test_get_url_not_found(client, url_object):
    """Test that 404 is returned if the shortcut is wrong."""
    response = client.get(reverse(URL_DETAIL_VIEW_NAME, args=("unknown",)))
    assert response.status_code == 404


@pytest.mark.django_db
def test_redirect(client, shortcut, original_url, url_object):
    """Test that resolving shortcut into original URL works."""
    response = client.get(reverse(RESOLVE_URL_VIEW_NAME, args=(shortcut,)), follow=False)
    assert response.status_code == 302
    assert response.url == original_url


@pytest.mark.django_db
def test_redirect_invalid_shortcut(client, url_object):
    """Test that 404 is raised if non-existing shortcut is attempted to be resolved."""
    response = client.get(reverse(RESOLVE_URL_VIEW_NAME, args=("unknown",)), follow=False)
    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize("n_uses", [0, 1, 5])
def test_redirect_update_url_usage(client, n_uses, shortcut, url_object):
    """Test that `use_count` and `last_accessed` attributes of URL are updated when it's resolved."""
    # Make sure it has default values.
    assert url_object.last_accessed is None
    assert url_object.use_count == 0

    for _ in range(n_uses):
        response = client.get(reverse(RESOLVE_URL_VIEW_NAME, args=(shortcut,)), follow=False)
        assert response.status_code == 302

    url_object.refresh_from_db()
    if n_uses > 1:
        assert url_object.last_accessed is not None
        assert isinstance(url_object.last_accessed, datetime)
    assert url_object.use_count == n_uses
