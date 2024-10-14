"""Utility functions for exporting DjangoHelpArticle instances to Markdown or ZIP."""

import io
import logging
import zipfile

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpResponse
from translated_fields import to_attribute

from django_help.models import DjangoHelpArticle


logger = logging.getLogger(__name__)


def article_to_markdown(article: DjangoHelpArticle) -> str:
    """Convert a DjangoHelpArticle instance to a Markdown string for each language."""
    tags = ",\n  - ".join(tag.name for tag in article.tags.all())
    relevant_paths = ", ".join(rp.path for rp in article.relevant_paths.all())

    metadata = {
        "id": str(article.id),
        "slug": article.slug,
        "views": article.views,
        "icon": article.icon,
        "public": article.public,
        "highlighted": article.highlighted,
        "intended_entity_type": article.intended_entity_type,
        "created": article.created.strftime("%Y-%m-%d %H:%M:%SZ"),
        "modified": article.modified.strftime("%Y-%m-%d %H:%M:%SZ"),
        "relevant_paths": relevant_paths,
        "tags": tags,
    }

    contents_dict = {}

    for lang_code, _ in settings.LANGUAGES:
        prefix = to_attribute("title", lang_code)
        metadata[f"title_{lang_code}"] = getattr(article, prefix, "")
        metadata[f"subtitle_{lang_code}"] = getattr(article, to_attribute("subtitle", lang_code), "")
        if article.category:
            metadata[f"category_title_{lang_code}"] = getattr(article.category, to_attribute("title", lang_code), "")
            metadata[f"category_subtitle_{lang_code}"] = getattr(
                article.category, to_attribute("subtitle", lang_code), ""
            )

        contents_dict[f"article_content_{lang_code}"] = getattr(article, to_attribute("article_content", lang_code), "")

    headers = "\n".join(f"{key}: {value}" for key, value in metadata.items())
    contents = "\n".join(
        f"# Translation {lang_code}\n{contents_dict[f'article_content_{lang_code}']}"
        for lang_code, _ in settings.LANGUAGES
    )

    return f"---\n{headers}\n---\n\n{contents}"


def export_articles_to_markdown_or_zip(queryset: QuerySet) -> HttpResponse:
    """Export the given queryset of DjangoHelpArticle instances to Markdown (.md) and/or ZIP (if multiple)."""
    if queryset.count() == 1:
        article = queryset.first()
        response = HttpResponse(article_to_markdown(article), content_type="text/markdown")
        response["Content-Disposition"] = f'attachment; filename="{article.slug}.md"'
        return response

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for article in queryset:
            md_content = article_to_markdown(article)
            zip_file.writestr(f"{article.slug}.md", md_content)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="articles.zip"'
    return response
