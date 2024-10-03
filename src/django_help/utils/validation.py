"""Validation utilities for the Django Help app."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Optional

from django.http import Http404
from django.http import HttpRequest


if TYPE_CHECKING:
    from django_help.models import DjangoHelpArticle


logger = logging.getLogger(__name__)


def user_authorized_to_view(request: HttpRequest, article: DjangoHelpArticle) -> Optional[Http404]:
    """Raises a 404 error if the user is not allowed to view the article."""
    if not request.user.is_staff:
        return

    if not (article.category and article.category.public and article.public):
        logger.warning("User %s attempted to view non-public article %s", request.user, article)
        raise Http404
