# core/domain/__init__.py
from .books import Book, BookCache, BookShelf
from .users import User, ActivityHistory
from .media import ExternalURL, YouTubeVideo
from .contact import Contact

__all__ = [
    # Books domain
    'Book',
    'BookCache',
    'BookShelf',

    # Users domain
    'User',
    'ActivityHistory',

    # Media domain
    'ExternalURL',
    'YouTubeVideo',

    # Contact domain
    'Contact',
]