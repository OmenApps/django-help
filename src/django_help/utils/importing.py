"""Utility functions for importing articles from Markdown files or ZIP archives."""

import logging
import os
import tempfile
import zipfile
from typing import Dict
from typing import Optional
from typing import Union

import frontmatter
from django.conf import settings
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from translated_fields import to_attribute

from django_help.forms import ArticleUploadForm
from django_help.models import DjangoHelpArticle
from django_help.models import DjangoHelpCategory


logger = logging.getLogger(__name__)


class ArticleManager:
    """Class to manage the creation and updating of DjangoHelpArticle instances from metadata and Markdown content."""

    def __init__(self):
        self.languages = settings.LANGUAGES

    def set_defaults(self, metadata: Dict) -> Dict:
        """Set default values from metadata."""
        defaults = {
            "slug": metadata["slug"],
            "views": metadata.get("views", 0) or 0,
            "public": metadata.get("public", True) if metadata.get("public") is not None else True,
            "highlighted": metadata.get("highlighted", False) if metadata.get("highlighted") is not None else False,
            "intended_entity_type": metadata.get("intended_entity_type", "any") or "any",
        }

        for lang_code, _ in self.languages:
            for field in ["title", "subtitle", "article_content"]:
                key = f"{field}_{lang_code}"
                defaults[to_attribute(field, lang_code)] = metadata.get(key, "") or ""
        return defaults

    def manage_categories(self, metadata: Dict, defaults: Dict) -> None:
        """Manage category creation or fetching.

        Uses the primary language title to create or fetch the category, and then sets the category for the article.
        """
        category_content = {}
        for lang_code, _ in self.languages:
            category_content[f"title_{lang_code}"] = metadata.get(f"category_title_{lang_code}", "") or ""
            category_content[f"subtitle_{lang_code}"] = metadata.get(f"category_subtitle_{lang_code}", "") or ""

        primary_language = settings.LANGUAGE_CODE
        if category_content.get(f"title_{primary_language}") is not None:
            category, _ = DjangoHelpCategory.objects.get_or_create(
                **{to_attribute("title", primary_language): category_content[f"title_{primary_language}"]},
                defaults={
                    key: val
                    for key, val in category_content.items()
                    if val and not key.startswith(f"title_{primary_language}")
                },
            )
            defaults["category"] = category

    def manage_relevant_paths(self, article: DjangoHelpArticle, metadata: Dict) -> None:
        """Clear and update relevant paths."""
        if "relevant_paths" in metadata and metadata["relevant_paths"] is not None:
            article.relevant_paths.all().delete()
            for path in metadata["relevant_paths"]:
                article.relevant_paths.get_or_create(path=path)

    def manage_tags(self, article: DjangoHelpArticle, metadata: Dict) -> None:
        """Update article tags."""
        tags = metadata.get("tags")
        if tags is not None:
            article.tags.set(tags, clear=True)

    def update_or_create_article(self, metadata: Dict) -> tuple[Optional[DjangoHelpArticle], bool]:
        """Update or create a DjangoHelpArticle instance from metadata."""
        if "id" not in metadata or "slug" not in metadata:
            logger.error("Required fields 'id' or 'slug' are missing.")
            return None, False

        with transaction.atomic():
            defaults = self.set_defaults(metadata)

            self.manage_categories(metadata, defaults)

            article, created = DjangoHelpArticle.objects.update_or_create(id=metadata["id"], defaults=defaults)
            self.manage_relevant_paths(article, metadata)
            self.manage_tags(article, metadata)

        return article, created

    def read_markdown_content(self, markdown_file: Union[str, tempfile.SpooledTemporaryFile]) -> str:
        """Read markdown content from a file or file-like object."""
        if isinstance(markdown_file, str):
            with open(markdown_file, "r", encoding="utf-8") as file:
                return file.read()
        else:
            return markdown_file.read().decode("utf-8")

    def extract_language_contents(self, content: str) -> Dict:
        """Extract and map content to languages based on headers in the markdown."""
        contents = content.split("\n# Translation ")
        logger.info("Extracted %s language contents from markdown.", len(contents))
        for idx, content in enumerate(contents):
            logger.info("Content %s: %s...", idx, content[:100])

        language_contents = {}

        # Handle the default language content
        default_lang_code = settings.LANGUAGE_CODE
        if contents:
            language_contents[default_lang_code] = contents[0].strip()

        # Handle translated content
        for content in contents[1:]:
            header_end_idx = content.find("\n")
            if header_end_idx != -1:
                lang_code = content[:header_end_idx].strip()
                content_body = content[header_end_idx + 1 :].strip()  # Start reading content after the newline
                if lang_code in dict(self.languages).keys():  # Ensure the language code is recognized
                    language_contents[lang_code] = content_body

        return language_contents

    def process_markdown_metadata(self, markdown_content: str) -> Optional[Dict]:
        """Parse markdown content and prepare metadata including language-specific content."""
        try:
            post = frontmatter.loads(markdown_content)
            metadata = post.metadata
            language_contents = self.extract_language_contents(post.content)
            for lang_code, content in language_contents.items():
                metadata[f"article_content_{lang_code}"] = content
            return metadata
        except KeyError as e:
            logger.error("Error parsing frontmatter: %s", e)
            return None

    def process_md_file(self, markdown_file: Union[str, tempfile.SpooledTemporaryFile]) -> bool:
        """Process a markdown file and create or update a DjangoHelpArticle instance."""
        markdown_content = self.read_markdown_content(markdown_file)
        logger.info("Processing markdown content starting with: %s...", markdown_content[:100])

        metadata = self.process_markdown_metadata(markdown_content)
        if metadata is None:
            return False

        self.update_or_create_article(metadata)
        return True

    def handle_zip_file(self, zip_file: Union[str, tempfile.SpooledTemporaryFile]) -> None:
        """Extract and process each Markdown file in a ZIP archive."""
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            with tempfile.TemporaryDirectory() as tempdir:
                zip_ref.extractall(tempdir)
                for file_name in zip_ref.namelist():
                    if file_name.lower().endswith(".md"):
                        full_path = os.path.join(tempdir, file_name)
                        self.process_md_file(full_path)
                    else:
                        logger.warning("Skipped non-Markdown file: %s", file_name)


@csrf_exempt
def upload_articles(request: HttpRequest):
    """Insert upload handler before processing uploaded files.

    We must ensure here that uploaded files are handled as temporary files
    See: https://docs.djangoproject.com/en/5.1/topics/http/file-uploads/#modifying-upload-handlers-on-the-fly
    """
    request.upload_handlers.insert(0, TemporaryFileUploadHandler(request))
    return _upload_articles(request)


@csrf_protect
def _upload_articles(request: HttpRequest):
    """Handles the uploading of articles in Markdown or ZIP format by administrators.

    Accessible only via POST method in an admin-specific view.
    """
    if request.method != "POST":
        return _handle_get_request(request)

    return _handle_post_request(request)


def _handle_get_request(request: HttpRequest):
    """Render the empty form for GET requests."""
    template = "django_help/admin/upload_articles.html"
    form = ArticleUploadForm()
    return render(request, template, {"form": form})


def _handle_post_request(request: HttpRequest):
    """Process the file upload through POST request."""
    template = "django_help/admin/upload_articles.html"
    form = ArticleUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, template, {"form": form})

    uploaded_file = form.cleaned_data.get("upload")
    if not uploaded_file:
        # Handle the case where the file is not provided
        form.add_error("upload", "Please upload a file.")
        return render(request, template, {"form": form})

    # Process the file based on its type
    article_manager = ArticleManager()
    if uploaded_file.name.endswith(".zip"):
        article_manager.handle_zip_file(uploaded_file)
    else:
        article_manager.process_md_file(uploaded_file)

    return redirect("admin:index")
