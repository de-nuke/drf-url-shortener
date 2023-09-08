import pytest

from shortener import constants, shortcuts
from shortener.factories import URLFactory
from shortener.models import URL


@pytest.fixture
def original_url() -> str:
    return "https://example.com/"


@pytest.fixture
def shortcut() -> str:
    return "testtest"


@pytest.fixture
def url_object(shortcut: str, original_url: str) -> URL:
    return URLFactory(shortcut=shortcut, original=original_url)


@pytest.fixture
def existing_shortcuts(faker):
    """Prepare as many existing short as there are attempts in shortcut generation.

    In other words, for each possible shortcut length, prepare SAME_LENGTH_ATTEMPTS shortcuts. When
    "generate_random_slug" is mocked to produce only those existing shortcuts, then shortcut generation will eventually
    raise GenerationError.
    """
    existing_shortcuts = []
    for length in range(constants.MIN_SHORTCUT_LENGTH, constants.MAX_SHORTCUT_LENGTH + 1):
        existing_shortcuts.extend(
            faker.pystr(min_chars=length, max_chars=length) for _ in range(shortcuts.SAME_LENGTH_ATTEMPTS)
        )

    for shortcut in existing_shortcuts:
        URLFactory(shortcut=shortcut)

    return existing_shortcuts
