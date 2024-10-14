"""Models for django_help."""

import logging
from typing import List
from typing import Union

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.http import HttpRequest
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField
from taggit.managers import TaggableManager
from taggit.models import ItemBase
from taggit.models import TagBase
from translated_fields import TranslatedField

from django_help.app_settings import BASE_FOREIGN_KEY_FIELD
from django_help.app_settings import BASE_MANAGER
from django_help.app_settings import BASE_MODEL
from django_help.app_settings import BASE_QUERYSET
from django_help.app_settings import EXTRA_LANGUAGES
from django_help.choices import IntendedEntityType
from django_help.utils.regex import get_path_regex


logger = logging.getLogger(__name__)

language_codes = [code for code, _ in settings.LANGUAGES]


def get_only_filters():
    """Return the fields to select in a queryset."""
    current_language_code = get_language()
    return [
        f"title_{current_language_code}",
        f"subtitle_{current_language_code}",
        "slug",
        "modified",
    ]


class Tag(TagBase, BASE_MODEL):
    """Customized Taggit Tag model."""

    class Meta(BASE_MODEL.Meta if hasattr(BASE_MODEL, "Meta") else object):
        """Meta options for Tag."""

        verbose_name = _("tag")
        verbose_name_plural = _("tags")


class DjangoHelpCategoryQuerySet(BASE_QUERYSET):
    """QuerySet for DjangoHelpCategory."""

    def public(self):
        """Return only categories which are public."""
        return self.filter(public=True)

    def private(self):
        """Return only categories which are not public."""
        return self.filter(public=False)

    def intended_for_any(self):
        """Return categories intended for any entity."""
        return self.filter(intended_entity_type=IntendedEntityType.ANY)


class DjangoHelpCategoryManager(BASE_MANAGER):
    """Manager for DjangoHelpCategory."""

    def get_queryset(self):
        """Return the queryset for this manager."""
        return super().get_queryset().all()


class DjangoHelpCategory(BASE_MODEL):
    """Stores categories."""

    title = TranslatedField(
        models.CharField(
            _("Title"),
            max_length=30,  # Specifically to fit the cards in the django_help index page
            help_text=_("The title of this category."),
            blank=True,
        ),
        EXTRA_LANGUAGES,
    )
    subtitle = TranslatedField(
        models.CharField(
            _("Subtitle"),
            max_length=70,
            blank=True,
            help_text=_("A subtitle for this category."),
        ),
        EXTRA_LANGUAGES,
    )
    slug = models.SlugField(
        _("Slug"),
        max_length=50,
        unique=True,
        help_text=_("A web address friendly version of the title."),
    )
    description = TranslatedField(
        models.CharField(
            _("Description"),
            max_length=200,
            blank=True,
            help_text=_("A description of this category."),
        ),
        EXTRA_LANGUAGES,
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("The icon and text color to use for this category."),
        default="fa-circle-info text-success",
    )
    public = models.BooleanField(
        default=True,
        help_text=_("Check this box to make this category public."),
    )

    intended_entity_type = models.CharField(
        max_length=20,
        choices=IntendedEntityType.choices,
        default=IntendedEntityType.ANY,
        help_text=_("The type of entity this category applies to."),
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = DjangoHelpCategoryManager.from_queryset(DjangoHelpCategoryQuerySet)()

    class Meta(BASE_MODEL.Meta if hasattr(BASE_MODEL, "Meta") else object):
        """Meta options for DjangoHelpCategory."""

        verbose_name = _("DjangoHelp Category")
        verbose_name_plural = _("DjangoHelp Categories")
        ordering = [f"title_{settings.LANGUAGE_CODE}"]  # Default to the primary language
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title

    @property
    def short_description(self, length=50):
        """Return a short description of this category."""
        return self.description[:length] + "..." if len(self.description) > length else self.description

    def add_article(self, article):
        """Add the specified article to this category."""
        article.category = self
        article.save()

    @staticmethod
    def remove_article(article):
        """Remove the specified article from its category."""
        article.category = None
        article.save()

    @property
    def article_count(self):
        """Return the number of article in this category."""
        return self.articles.count()


class TaggedArticles(ItemBase, BASE_MODEL):
    """Stores tagged articles."""

    content_object = BASE_FOREIGN_KEY_FIELD(
        "django_help.DjangoHelpArticle",
        on_delete=models.CASCADE,
    )
    tag = BASE_FOREIGN_KEY_FIELD(
        Tag,
        related_name="%(app_label)s_%(class)s_items",
        on_delete=models.CASCADE,
    )

    class Meta(BASE_MODEL.Meta if hasattr(BASE_MODEL, "Meta") else object):
        """Meta options for TaggedArticles."""

        verbose_name = _("Tagged Article")
        verbose_name_plural = _("Tagged Articles")


class DjangoHelpArticleQuerySet(BASE_QUERYSET):
    """QuerySet for DjangoHelpArticle."""

    def public(self):
        """Return only article which is public."""
        return self.filter(public=True)

    def private(self):
        """Return only article which is not public."""
        return self.filter(public=False)

    def intended_for_any(self):
        """Return article intended for any entity."""
        return self.filter(intended_entity_type=IntendedEntityType.ANY)

    def search(self, search_terms: List[str]):
        """Search for article matching the specified query in the current language."""
        if len(search_terms) == 0:
            return self.none()

        # For each search term, create filters in the current language.
        title_filters = {f"title_{get_language()}__icontains": search_term for search_term in search_terms}
        subtitle_filters = {f"subtitle_{get_language()}__icontains": search_term for search_term in search_terms}
        article_content_filters = {
            f"article_content_{get_language()}__icontains": search_term for search_term in search_terms
        }
        tags_filters = {"tags__name__icontains": search_term for search_term in search_terms}

        filters = Q(**title_filters) | Q(**subtitle_filters) | Q(**article_content_filters) | Q(**tags_filters)
        logger.debug("Called search in DjangoHelpArticleQuerySet with filters: %s", filters)
        return self.filter(filters)

    def get_for_tag(self, tag: str, multiple=False):
        """Return article(s) matching the specified tag.

        If `single` is True (default), return only the first article.
        """
        qs = self.filter(tags__name__in=[tag])
        if multiple:
            return qs
        return qs.first()

    def get_for_category(self, category: str, multiple=False):
        """Return article(s) matching the specified category.

        If `single` is True (default), return only the first article.
        """
        title_filters = {f"category__title_{code}__icontains": category.lower() for code in language_codes}
        slug_filters = {"category__slug__icontains": category.lower()}

        filters = Q(**title_filters) | Q(**slug_filters)
        logger.debug("Called get_for_category in DjangoHelpArticleQuerySet with filters: %s", filters)
        qs = self.filter(filters)
        if multiple:
            return qs
        return qs.first()

    def get_for_slug(self, slug: str, multiple=False):
        """Return article(s) matching the specified slug.

        If `single` is True (default), return only the first article.
        """
        qs = self.filter(slug__iexact=slug.lower())
        if multiple:
            return qs
        return qs.first()

    def get_for_path(self, path: Union[str, HttpRequest], multiple=False):
        """Return article(s) matching the specified path.

        If `single` is True (default), return only the first article.
        """
        qs = self.filter(relevant_paths__path__iregex=get_path_regex(path))
        if multiple:
            return qs
        return qs.first()

    def top_three_popular(self):
        """Return the top three most viewed articles."""
        return self.order_by("-views").only(*get_only_filters())[:3]

    def top_three_highlighted(self):
        """Return the top three most viewed articles which are highlighted."""
        return self.filter(highlighted=True).order_by("-views").only(*get_only_filters())[:3]

    def top_three_recent(self):
        """Return the top three most recent articles."""
        return self.order_by("-created").only(*get_only_filters())[:3]


class DjangoHelpArticleManager(BASE_MANAGER):
    """Manager for DjangoHelpArticle."""

    def get_queryset(self):
        """Return the queryset for this manager."""
        return super().get_queryset().all()


class DjangoHelpArticle(BASE_MODEL):
    """Stores articles."""

    title = TranslatedField(
        models.CharField(
            _("Title"),
            max_length=30,
            blank=True,
            help_text=_("The title of this article."),
        ),
        EXTRA_LANGUAGES,
    )
    subtitle = TranslatedField(
        models.CharField(
            _("Subtitle"),
            max_length=70,
            blank=True,
            help_text=_("A subtitle for this article."),
        ),
        EXTRA_LANGUAGES,
    )
    slug = models.SlugField(
        _("Slug"),
        max_length=50,
        unique=True,
        help_text=_("A web address friendly version of the title."),
    )
    category = BASE_FOREIGN_KEY_FIELD(
        DjangoHelpCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="articles",
        help_text=_("The category this article belongs to, if any."),
    )

    article_content = TranslatedField(
        MarkdownxField(
            _("Article Content"),
            help_text=_("The content of this article. Markdown is supported."),
            blank=True,
        ),
        EXTRA_LANGUAGES,
    )

    views = models.PositiveIntegerField(
        default=0,
        help_text=_("The number of times this article has been viewed."),
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("The icon and text color to use for this article."),
        default="fa-circle-info text-success",
    )
    public = models.BooleanField(
        default=True,
        help_text=_("Check this box to make this article public."),
    )
    highlighted = models.BooleanField(
        default=False,
        help_text=_("Check this box to highlight this article on the index page."),
    )

    intended_entity_type = models.CharField(
        max_length=20,
        choices=IntendedEntityType.choices,
        default=IntendedEntityType.ANY,
        help_text=_("The type of entity this article applies to."),
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = DjangoHelpArticleManager.from_queryset(DjangoHelpArticleQuerySet)()

    tags = TaggableManager(
        through=TaggedArticles,
        blank=True,
        help_text=_("A comma-separated list of tags."),
    )

    class Meta(BASE_MODEL.Meta if hasattr(BASE_MODEL, "Meta") else object):
        """Meta options for DjangoHelpArticle."""

        verbose_name = _("DjangoHelp Article")
        verbose_name_plural = _("DjangoHelp Articles")
        ordering = [f"title_{settings.LANGUAGE_CODE}"]  # Default to the primary language
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def clean(self):
        """Ensure the intended entity type matches the category's intended entity type."""
        if self.category and not (
            self.intended_entity_type == self.category.intended_entity_type
            or self.intended_entity_type == IntendedEntityType.ANY
            or self.category.intended_entity_type == IntendedEntityType.ANY
        ):
            validation_error_message = _(
                f"The intended entity type of this article must match the category's intended entity "
                f"type or be any. {self.intended_entity_type=} {self.category.intended_entity_type=}."
            )
            raise ValidationError(validation_error_message)
        super().clean()

    def __str__(self):
        return self.title

    def add_relevant_path(self, path: str):
        """Add the specified path to this article."""
        RelevantPath.objects.create(path=path, article=self)

    def content_preview(self, length=100):
        """Return a preview of the content, truncated to the specified length."""
        return self.article_content[:length] + "..." if len(self.article_content) > length else self.article_content


class RelevantPath(BASE_MODEL):
    """Stores a relevant path for an article.

    A relevant path is a path that is relevant to the article. For example, if the article is about
    creating a new provider, then the relevant path might be `/providers/create`.

    Wildcards are supported. For example, if the article is about creating a new provider, then the relevant
    path might be `/providers/*`.
    """

    path = models.CharField(
        max_length=200,
        help_text=_("The relevant path for this article. Wildcards are supported."),
    )
    article = BASE_FOREIGN_KEY_FIELD(
        DjangoHelpArticle,
        on_delete=models.CASCADE,
        related_name="relevant_paths",
    )

    class Meta(BASE_MODEL.Meta if hasattr(BASE_MODEL, "Meta") else object):
        """Meta options for RelevantPath."""

        verbose_name = _("Relevant Path")
        verbose_name_plural = _("Relevant Paths")
        ordering = ["path"]
        indexes = [
            models.Index(fields=["path"]),
        ]

    def __str__(self):
        return str(self.path)

    @property
    def is_wildcard(self):
        """Return True if the path is a wildcard path."""
        return "*" in list(self.path)


class ArticleUpload(BASE_MODEL):
    """Stores uploaded files for articles."""

    upload = models.FileField(upload_to="uploads/%Y/%m/%d/")

    class Meta:
        """Meta options for ArticleUpload."""

        managed = False  # No database table creation or deletion operations will be performed for this model.
        verbose_name = _("DjangoHelp Article Upload")
        verbose_name_plural = _("DjangoHelp Article Uploads")

    @property
    def filename(self):
        """Return the filename of the upload."""
        return self.upload.name.split("/")[-1]

    @property
    def extension(self):
        """Return the extension of the upload."""
        return self.filename.split(".")[-1]

    def __str__(self):
        return self.filename
