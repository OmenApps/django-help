"""Queryset utilities for the Django Help app."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Union
from urllib.parse import unquote

from django.db.models import F
from django.http import HttpRequest
from translated_fields import to_attribute

from django_help.models import DjangoHelpArticle


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from django_help.models import DjangoHelpArticleQuerySet
    from django_help.models import DjangoHelpCategoryQuerySet


def filter_user_can_view(
    request: HttpRequest, articles_or_categories: Union[DjangoHelpArticleQuerySet, DjangoHelpCategoryQuerySet]
) -> Union[DjangoHelpArticleQuerySet, DjangoHelpCategoryQuerySet]:
    """Filters QuerySet to return only public articles or categories based on the user's entity context."""
    if request.user.is_staff:
        return articles_or_categories
    if request.entity_context.id == request.provider_context.id:
        return articles_or_categories.intended_for_providers_or_any().public()
    return articles_or_categories.intended_for_consumers_or_any().public()


def filter_articles(request: HttpRequest, category: str, slug: str, tag: str) -> DjangoHelpArticleQuerySet:
    """Filters articles based on user permissions and provided parameters.

    Note: This is a helper function for get_articles.
    """
    logger.info(
        "Called get_filtered_articles for: %s, %s, %s, %s, %s, %s",
        category,
        type(category),
        slug,
        type(slug),
        tag,
        request.path,
    )

    articles = filter_user_can_view(request, DjangoHelpArticle.objects.all())

    if tag is not None:
        logger.info("Getting articles for: %s", tag)
        articles = articles.get_for_tag(unquote(tag), multiple=True)
    elif slug is not None:
        logger.info("Getting articles for: %s", slug)
        articles = articles.get_for_slug(unquote(slug), multiple=True)
    elif category is not None:
        logger.info("Getting articles for: %s", category)
        articles = articles.get_for_category(unquote(category), multiple=True)
    else:
        logger.info("Getting articles for: %s", request.path)
        articles = articles.get_for_path(request.path, multiple=True)

    if not request.user.is_staff:
        articles = articles.public()

    return articles


def annotate_with_values_fields(queryset, values_fields: list[str]):
    """Annotates the queryset with the values fields.

    For instance, if values_fields = ["title"], the queryset will be annotated with `title=to_attribute("title")`,
      ensuring the current language is used. e.g.: If the currentl language is 'en', the annotation will convert
      `title_en` to `title`.
    """
    return queryset.annotate(**{field: F(to_attribute(field)) for field in values_fields})
