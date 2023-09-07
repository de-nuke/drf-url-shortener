import contextlib
from unittest import mock

from django.conf import settings
from django.urls import URLResolver
from django.urls.resolvers import RegexPattern


@contextlib.contextmanager
def mock_url_patterns(urlpatterns):
    """Mock URL patterns in the application.

    It is required to monkeypatch "get_resolver" function so that it builds a new URLResolver everytime rather than
    using LRU cache. Otherwise, urlpatterns used for the first time, will be cached and always returned instead of the
    newer ones.
    """

    def get_resolver_mock(urlconf):
        if urlconf is None:
            urlconf = settings.ROOT_URLCONF
        return URLResolver(RegexPattern(r"^/"), urlconf)

    with mock.patch("drf_url_shortener.urls.urlpatterns", urlpatterns) as mocked_patterns:
        with mock.patch("django.urls.base.get_resolver", get_resolver_mock):
            yield mocked_patterns
