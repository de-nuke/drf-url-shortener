from unittest import mock

import pytest
import pytest_django.asserts

from shortener import constants, shortcuts
from shortener.factories import URLFactory


@pytest.mark.parametrize("length", [-1, 0, 1, 10, 100])
def test_get_random_slu_(length):
    """Test `shortener.shortcuts.get_random_slug`.

    Check that generated string is of correct length and has no forbidden characters.
    """
    slug = shortcuts.get_random_slug(length)
    if length == -1:
        assert len(slug) == 0
    else:
        assert len(slug) == length

    for s in slug:
        assert s in shortcuts.CHARSET, f"Found invalid character in generated slug: '{s}'"


@pytest.mark.django_db
def test_get_shortcut_shortcut_found(faker):
    """Test `shortener.shortcuts.get_shortcut`.

    Check that it returns unique, non-existing shortcut
    """
    existing_shortcuts = [
        faker.pystr(min_chars=constants.MIN_SHORTCUT_LENGTH, max_chars=constants.MAX_SHORTCUT_LENGTH) for _ in range(3)
    ]
    non_existing_shortcut = faker.pystr(
        min_chars=constants.MIN_SHORTCUT_LENGTH, max_chars=constants.MAX_SHORTCUT_LENGTH
    )
    for shortcut in existing_shortcuts:
        URLFactory(shortcut=shortcut)

    # Generate shortcut that already exists for 3 times in a row, then finally generate non-existing one.
    with mock.patch("shortener.shortcuts.get_random_slug", side_effect=[*existing_shortcuts, non_existing_shortcut]):
        # Each shortcut had to be tested if it exists
        with pytest_django.asserts.assertNumQueries(len(existing_shortcuts) + 1):
            shortcut = shortcuts.get_shortcut()

    assert shortcut == non_existing_shortcut


@pytest.mark.django_db
def test_get_shortcut_shortcut_not_found(faker):
    """Test `shortener.shortcuts.get_shortcut`.

    Check that it raises `GenerationError` if it was unable to find shortcut in several attempts.
    """
    existing_shortcuts = []
    for length in range(constants.MIN_SHORTCUT_LENGTH, constants.MAX_SHORTCUT_LENGTH + 1):
        existing_shortcuts.extend(
            faker.pystr(min_chars=length, max_chars=length) for _ in range(shortcuts.SAME_LENGTH_ATTEMPTS)
        )

    for shortcut in existing_shortcuts:
        URLFactory(shortcut=shortcut)

    # Mock "get_random_slug" to always return an existing slug
    with mock.patch("shortener.shortcuts.get_random_slug", side_effect=existing_shortcuts):
        # Each shortcut had to be tested if it exists
        with pytest_django.asserts.assertNumQueries(len(existing_shortcuts)):
            with pytest.raises(shortcuts.GenerationError):
                shortcuts.get_shortcut()
