"""Defines custom template tags for django_help."""

import markdown as md
from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def load_dependencies():
    """Loads the dependencies for django_help."""
    css_url = static("django_help/css/styles.css")
    # return mark_safe(
    #     f"""
    #     <!-- Include AlpineJS -->
    #     <script src="https://cdn.jsdelivr.net/npm/alpinejs@2" defer></script>
    #     <!-- Include htmx -->
    #     <script src="https://unpkg.com/htmx.org/dist/htmx.js"></script>
    #     <!-- Include custom css -->
    #     <link href="{css_url}" rel="stylesheet">
    #     """
    # )
    return mark_safe(
        f"""
        <!-- Include custom css -->
        <link href="{css_url}" rel="stylesheet">
        """
    )


@register.filter(name="markdown")
def markdown_format(text):
    """Formats the given text as markdown."""
    return md.markdown(text, extensions=["markdown.extensions.fenced_code"])


@register.inclusion_tag("django_help/fragments/button_slug.html")
def django_help_slug(slug, title=None):
    """Renders a django_help button with the given slug."""
    return {"slug": slug, "title": title}


@register.inclusion_tag("django_help/fragments/button_category.html")
def django_help_category(category, title=None):
    """Renders a django_help button with the given category."""
    return {"category": category, "title": title}


@register.inclusion_tag("django_help/fragments/button_tag.html")
def django_help_tag(tag, title=None):
    """Renders a django_help button with the given tag."""
    return {"tag": tag, "title": title}


@register.inclusion_tag("django_help/fragments/button_current_path.html")
def django_help_current_path(title=None):
    """Renders a django_help button with the given current path."""
    return {"title": title}
