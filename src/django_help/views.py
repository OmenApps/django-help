"""Views for django_help."""

import logging

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import Q
from django.http import Http404
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from translated_fields import to_attribute

from django_help.app_settings import AUTHORIZE_USER_TO_VIEW_ARTICLE
from django_help.forms import DjangoHelpArticleForm
from django_help.models import DjangoHelpArticle
from django_help.models import DjangoHelpCategory
from django_help.utils.queryset import annotate_with_values_fields
from django_help.utils.queryset import filter_articles
from django_help.utils.queryset import filter_user_can_view


logger = logging.getLogger(__name__)


@login_required
def index(request: HttpRequest) -> TemplateResponse:
    """The main django_help page.

    Provides:
    - a search box
    - an option for admins to create new articles
    - a list of popular articles
    - a list of highlighted articles, and
    - a list of recent articles.
    """
    template = "django_help/pages-index.html"
    context = {}
    context["url"] = request.path
    queryset = DjangoHelpArticle.objects.all()

    base_article_qs = filter_user_can_view(request, queryset)

    categories = DjangoHelpCategory.objects.annotate(
        number_of_articles=Count("articles", filter=Q(articles__public=True))
    )
    categories = filter_user_can_view(request, categories)

    context["popular_articles"] = base_article_qs.top_three_popular()
    context["highlighted_articles"] = base_article_qs.top_three_highlighted()
    context["recent_articles"] = base_article_qs.top_three_recent()
    context["categories"] = categories.order_by(to_attribute("title"))

    if not request.user.is_staff:
        queryset = queryset.public()

    queryset = queryset.order_by("-modified")

    search_query = request.GET.get("search", "").strip()
    if search_query:
        search_keywords = search_query.lower().split(",")
        query = list(map(str.strip, search_keywords))
        queryset = queryset.search(query)

        # Paginate the queryset
        paginator = Paginator(queryset, 9)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
        context["articles"] = page_obj
        context["is_paginated"] = page_obj.has_other_pages()

    return TemplateResponse(request, template, context)


@login_required
def category(request: HttpRequest, category_slug: str) -> TemplateResponse:
    """The category page for django_help.

    Provides:
    - a list of categories
    - a list of articles in the current category
    """
    template = "django_help/pages-category.html"
    context = {}
    current_category = get_object_or_404(DjangoHelpCategory, slug=category_slug)

    if request.user.is_staff:
        articles_in_current_category = current_category.articles.all()
        categories = DjangoHelpCategory.objects.all()
    else:
        articles_in_current_category = filter_user_can_view(request, current_category.articles.all())
        categories = filter_user_can_view(request, DjangoHelpCategory.objects.all())

    # Annotate with `title` field
    values_fields = ["title"]
    articles_in_current_category = annotate_with_values_fields(articles_in_current_category, values_fields)
    categories = annotate_with_values_fields(categories, values_fields)

    articles_in_current_category = articles_in_current_category.order_by("title").values("title", "slug")
    categories = categories.order_by("title").values("title", "slug")

    context["current_category"] = current_category
    context["articles_in_current_category"] = articles_in_current_category
    context["categories"] = categories

    return TemplateResponse(request, template, context)


@login_required
def view_article(request: HttpRequest, article_slug: str) -> TemplateResponse:
    """Uses htmx to load a specific article instance based on the slug."""
    if "HTTP_HX_REQUEST" in request.META and request.META["HTTP_HX_REQUEST"] == "true":
        context = {}
        template = "django_help/fragments/modal_content.html"

        article = DjangoHelpArticle.objects.filter(slug=article_slug).first()
        AUTHORIZE_USER_TO_VIEW_ARTICLE(request, article)

        if request.user.is_staff and article is None:
            template = "django_help/fragments/create_article.html"
            form = DjangoHelpArticleForm()
            context["form"] = form
        else:
            context["article"] = article
            if article is None:
                logger.error("Article with slug %s not found", article_slug)
                raise Http404

        return TemplateResponse(request, template, context)
    logger.error("Request to view article %s was not an htmx request", article_slug)
    raise Http404


@login_required
def get_articles(request: HttpRequest, *, category: str = None, slug: str = None, tag: str = None) -> TemplateResponse:
    """Fetches articles based on category, slug, or tag."""
    logger.info("Called get_articles for: %s, %s, %s, %s", category, slug, tag, request.path)
    context = {}
    articles = filter_articles(request, category, slug, tag)

    if articles.exists():
        articles = articles.distinct()
    else:
        logger.warning("No articles found for: %s, %s, %s, %s", category, slug, tag, request.path)
        articles = filter_user_can_view(request, DjangoHelpArticle.objects.all().distinct())

    context["article"] = first_article = articles.first()
    context["articles"] = articles.exclude(id=first_article.id).top_three_popular()

    template = "django_help/fragments/modal_content.html"

    return TemplateResponse(request, template, context)


@login_required
@staff_member_required
def create_article(request):
    """Creates a new article instance."""
    template = "django_help/fragments/create_article.html"
    context = {}

    if request.method == "POST":
        form = DjangoHelpArticleForm(request.POST)

        if form.is_valid():
            article = form.save()
            context["article"] = article
            template = "django_help/fragments/modal_content.html"
            messages.success(request, "Article created successfully!")
            return TemplateResponse(request, template, context)
        else:
            context["form"] = form
            return TemplateResponse(request, template, context)

    form = DjangoHelpArticleForm()

    context["form"] = form
    return TemplateResponse(request, template, context)


@login_required
@staff_member_required
def edit_article(request, article_slug):
    """Edits an existing article instance."""
    article = get_object_or_404(DjangoHelpArticle, slug=article_slug)

    context = {}
    context["article"] = article

    template = "django_help/fragments/edit_article.html"
    success_template = "django_help/fragments/modal_content.html"

    if request.method == "POST":
        form = DjangoHelpArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Article modified successfully!")
            return TemplateResponse(request, success_template, context)
        else:
            context["form"] = form
            return TemplateResponse(request, template, context)
    else:
        form = DjangoHelpArticleForm(instance=article)
        context["form"] = form
        return TemplateResponse(request, template, context)
