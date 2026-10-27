from flask import Blueprint

web = Blueprint("web", __name__)

from . import (  # noqa: E402
    auth,
    book,
    drift,
    gift,
    main,
    wish,
)

__all__ = ["main", "book", "auth", "drift", "gift", "wish"]
