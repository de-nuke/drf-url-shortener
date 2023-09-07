import random
import string

from shortener import constants
from shortener.models import URL

CHARSET = string.ascii_letters + string.digits
SAME_LENGTH_ATTEMPTS = 10


class GenerationError(Exception):
    pass


def get_random_slug(length: int) -> str:
    """Get random ASCII string of given length."""
    return "".join(random.SystemRandom().choice(CHARSET) for _ in range(length))


def get_shortcut() -> str:
    """Generate unique and non-existing string that can be used as a URL shortcut.

    Shortcut generation algorithm tries to find a shortcut with given length in 10 attempts.
    If all attempts for this particular length fail, then it means that there are already probably a lot of
    shortcuts with such length (because otherwise it's nearly impossible to generate 10 strings in a row that already
    exists). In such case, we can try 10 times to generate 1-char longer shortcut again.

    When there are already billions of entries in the database, this approach allows us to find an available
    shortcut much faster than if we wanted to generate all possible 5-char shortcuts first at all costs,
    only then check all 6-character ones, etc.

    In the worst case scenario, 60 random slugs will be tried and in theory, each of them can be taken. In this case
    we simply throw GenerationError and user should try again. However, this is so unlikely to happen, that it's we
    don't have to handle this case.
    """
    shortcut_length = constants.MIN_SHORTCUT_LENGTH
    shortcut = get_random_slug(shortcut_length)
    attempt = 1
    while URL.objects.filter(shortcut=shortcut).exists() or shortcut in constants.DISALLOWED_SHORTCUTS:
        if attempt >= SAME_LENGTH_ATTEMPTS:
            shortcut_length += 1
            attempt = 1
        else:
            attempt += 1

        if shortcut_length > constants.MAX_SHORTCUT_LENGTH:
            raise GenerationError("Failed to found unique shortcut. Try again.")

        shortcut = get_random_slug(shortcut_length)

    return shortcut
