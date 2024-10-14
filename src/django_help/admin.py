"""Admin configuration for django_help."""

import logging

from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from markdownx.admin import MarkdownxModelAdmin
from translated_fields import TranslatedFieldAdmin

from django_help.models import DjangoHelpArticle
from django_help.models import DjangoHelpCategory
from django_help.models import RelevantPath
from django_help.models import TaggedArticles
from django_help.utils.exporting import export_articles_to_markdown_or_zip
from django_help.utils.importing import upload_articles


logger = logging.getLogger(__name__)

installed_languages = [lang_code for lang_code, _ in settings.LANGUAGES]


@admin.register(TaggedArticles)
class TaggedArticlesAdmin(admin.ModelAdmin):
    """Admin configuration for TaggedArticles instances."""

    list_display = ("tag",)
    search_fields = ("tag",)


class RelevantPathInline(admin.TabularInline):
    """Inline for RelevantPath instances."""

    model = RelevantPath
    extra = 0


@admin.action(description="Export selected articles to Markdown (.md) and/or ZIP")
def export_articles(modeladmin, request, queryset):
    """Action to export the selected articles to Markdown (.md) and/or ZIP."""
    return export_articles_to_markdown_or_zip(queryset)


@admin.register(DjangoHelpCategory)
class DjangoHelpCategoryAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
    """Admin configuration for DjangoHelpCategory instances."""

    list_display = (
        f"title_{get_language()}",
        "slug",
        f"subtitle_{get_language()}",
        "icon",
        "intended_entity_type",
        "public",
        "created",
        "modified",
    )
    list_filter = ("public", "intended_entity_type")
    search_fields = (
        *[f"title_{lang_code}" for lang_code in installed_languages],
        *[f"subtitle_{lang_code}" for lang_code in installed_languages],
        *[f"description_{lang_code}" for lang_code in installed_languages],
        "slug",
    )
    readonly_fields = ("created", "modified")
    fieldsets = (
        (_("title"), {"fields": DjangoHelpCategory.title.fields}),
        (_("subtitle"), {"fields": DjangoHelpCategory.subtitle.fields}),
        (_("description"), {"fields": DjangoHelpCategory.description.fields}),
        (_(""), {"fields": ["slug", "icon", "intended_entity_type", "public", "created", "modified"]}),
    )
    prepopulated_fields = {"slug": (f"title_{get_language()}",)}


@admin.register(DjangoHelpArticle)
class DjangoHelpArticleAdmin(TranslatedFieldAdmin, MarkdownxModelAdmin):
    """Admin configuration for DjangoHelpArticle instances."""

    list_display = (
        f"title_{get_language()}",
        "slug",
        f"subtitle_{get_language()}",
        "category",
        "icon",
        "public",
        "highlighted",
        "intended_entity_type",
        "views",
        "tag_list",
        "created",
        "modified",
    )
    list_filter = ("public", "category", "intended_entity_type", "highlighted")
    search_fields = (
        *[f"title_{lang_code}" for lang_code in installed_languages],
        *[f"subtitle_{lang_code}" for lang_code in installed_languages],
        *[f"article_content_{lang_code}" for lang_code in installed_languages],
        "slug",
        "tags",
    )
    readonly_fields = ("created", "modified")
    inlines = [RelevantPathInline]
    actions = [export_articles]
    fieldsets = (
        (_("title"), {"fields": DjangoHelpArticle.title.fields}),
        (_("subtitle"), {"fields": DjangoHelpArticle.subtitle.fields}),
        (_("article_content"), {"fields": DjangoHelpArticle.article_content.fields}),
        (_(""), {"fields": ["category", "slug", "icon", "public", "highlighted", "intended_entity_type", "tags"]}),
    )
    prepopulated_fields = {"slug": (f"title_{get_language()}",)}

    def changelist_view(self, request, extra_context=None):
        """Add the upload button to the changelist view."""
        extra_context = extra_context or {}
        extra_context["show_upload_button"] = True
        extra_context["upload_url"] = "upload/"
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        """Add the upload view to the admin."""
        urls = super().get_urls()
        my_urls = [
            path("upload/", self.admin_site.admin_view(upload_articles), name="upload_articles"),
        ]
        return my_urls + urls

    def get_queryset(self, request):
        """Prefetch tags for the queryset."""
        return super().get_queryset(request).prefetch_related("tags")

    def tag_list(self, obj):
        """Return a comma-separated list of tags for the object."""
        return ", ".join(o.name for o in obj.tags.all())
