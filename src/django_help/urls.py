"""URLs for django_help."""

from django.urls import path

from django_help import views


app_name = "django_help"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_article, name="create_article"),
    path("category/<slug:category_slug>/", views.category, name="category"),
    path("article/<slug:article_slug>/edit/", views.edit_article, name="edit_article"),
    path("article/<slug:article_slug>/", views.view_article, name="view_article"),
    # The following paths all share the same name "get_articles" and are distinguished by the presence of the kwargs.
    # See: https://docs.djangoproject.com/en/dev/topics/http/urls/#naming-url-patterns
    path(
        "articles/category/<str:category>/",
        views.get_articles,
        name="get_articles",
    ),
    path(
        "articles/slug/<slug:slug>/",
        views.get_articles,
        name="get_articles",
    ),
    path(
        "articles/tag/<str:tag>/",
        views.get_articles,
        name="get_articles",
    ),
    path(
        "articles/",
        views.get_articles,
        name="get_articles",
    ),
]
