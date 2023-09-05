import factory

from shortener import constants
from shortener.models import URL


class URLFactory(factory.django.DjangoModelFactory):
    original = factory.Faker("url")
    shortcut = factory.Faker("pystr", min_chars=constants.MIN_SHORTCUT_LENGTH, max_chars=constants.MAX_SHORTCUT_LENGTH)

    class Meta:
        model = URL
