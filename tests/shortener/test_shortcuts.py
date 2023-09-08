from unittest import mock

import pytest
import pytest_django.asserts

from shortener import constants, shortcuts


@pytest.mark.parametrize("length", [-1, 0, 1, 10, 100])
def test_get_random_slug(length):
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
def test_get_shortcut_shortcut_found(existing_shortcuts, faker):
    """Test `shortener.shortcuts.get_shortcut`.

    Check that it returns unique, non-existing shortcut
    """
    non_existing_shortcut = faker.pystr(
        min_chars=constants.MIN_SHORTCUT_LENGTH, max_chars=constants.MAX_SHORTCUT_LENGTH
    )

    # Generate shortcut that already exists for 3 times in a row, then finally generate non-existing one.
    random_slugs = existing_shortcuts[:3] + [non_existing_shortcut]
    with mock.patch("shortener.shortcuts.get_random_slug", side_effect=random_slugs):
        # Each shortcut had to be tested if it exists
        with pytest_django.asserts.assertNumQueries(len(random_slugs)):
            shortcut = shortcuts.get_shortcut()

    assert shortcut == non_existing_shortcut


@pytest.mark.django_db
def test_get_shortcut_shortcut_not_found(existing_shortcuts):
    """Test `shortener.shortcuts.get_shortcut`.

    Check that it raises `GenerationError` if it was unable to find shortcut in several attempts.
    """
    # Mock "get_random_slug" to always return an existing slug
    with mock.patch("shortener.shortcuts.get_random_slug", side_effect=existing_shortcuts):
        # Each shortcut had to be tested if it exists
        with pytest_django.asserts.assertNumQueries(len(existing_shortcuts)):
            with pytest.raises(shortcuts.GenerationError):
                shortcuts.get_shortcut()
