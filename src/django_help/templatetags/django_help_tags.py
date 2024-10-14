"""Defines custom template tags for django_help."""

from collections.abc import Iterable

import markdown as md
from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe


register = template.Library()

try:
    # For Django 5.1 and above, we can import the querystring tag
    from django.template.defaulttags import querystring  # pylint: disable=W0611
except ImportError:
    # For Django 5.0 and below, we need to define the querystring tag

    @register.simple_tag(name="querystring", takes_context=True)
    def querystring(context, query_dict=None, **kwargs):
        """
        Add, remove, and change parameters of a ``QueryDict`` and return the result
        as a query string. If the ``query_dict`` argument is not provided, default
        to ``request.GET``.

        For example::

            {% querystring foo=3 %}

        To remove a key::

            {% querystring foo=None %}

        To use with pagination::

            {% querystring page=page_obj.next_page_number %}

        A custom ``QueryDict`` can also be used::

            {% querystring my_query_dict foo=3 %}
        """
        if query_dict is None:
            query_dict = context.request.GET
        query_dict = query_dict.copy()
        for key, value in kwargs.items():
            if value is None:
                if key in query_dict:
                    del query_dict[key]
            elif isinstance(value, Iterable) and not isinstance(value, str):
                query_dict.setlist(key, value)
            else:
                query_dict[key] = value
        if not query_dict:
            return ""
        query_string = query_dict.urlencode()
        return f"?{query_string}"


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
    """Formats the given text as markdown and processes internal links."""
    import re

    from django.urls import reverse
    from django.utils.safestring import mark_safe

    def replace_internal_links(match):
        slug = match.group(1)
        title = match.group(2) if match.group(2) else slug
        url = reverse("django_help:view_article", kwargs={"article_slug": slug})
        return f'<a href="{url}" class="internal-link" data-slug="{slug}">{title}</a>'

    # Convert markdown to HTML
    html = md.markdown(text, extensions=["markdown.extensions.fenced_code"])

    # Replace internal links with custom format
    pattern = r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]"
    html = re.sub(pattern, replace_internal_links, html)

    return mark_safe(html)


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
