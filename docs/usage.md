# Usage

## Configuration

### Settings

Configure django-help in your project's `settings.py`:

```python
DJANGO_HELP_CONFIG = {
    "EXTRA_LANGUAGES": {
        "es": {"blank": False},  # Spanish fields must be filled out
        "fr": {"blank": True},   # French fields can be left blank
    },
    "BASE_MANAGER": "myapp.managers.CustomManager",
    "BASE_QUERYSET": "myapp.querysets.CustomQuerySet",
    "BASE_MODEL": "myapp.models.CustomModel",
    "BASE_FOREIGN_KEY": "myapp.fields.CustomForeignKey",
    "AUTHORIZE_USER_TO_VIEW_ARTICLE": "myapp.utils.custom_authorization_function",
    "INTENDED_ENTITY_TYPE": {
        "PERSON": ("person", "Person"),
        "ORGANIZATION": ("organization", "Organization"),
    },
}
```

- `EXTRA_LANGUAGES`: Define additional languages and their field requirements.
- `BASE_MANAGER`, `BASE_QUERYSET`, `BASE_MODEL`, `BASE_FOREIGN_KEY`: Customize base classes for models and querysets. These are optional.
- `AUTHORIZE_USER_TO_VIEW_ARTICLE`: Custom function for article view authorization.
- `INTENDED_ENTITY_TYPE`: Define custom entity types for articles and categories.

### URLs

Include django-help URLs in your project's `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    ...
    path('help/', include('django_help.urls')),
]
```

### Templates

Add django-help tags to your `TEMPLATES` configuration:

```python
TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'django.template.context_processors.request',
            ],
            'builtins': [
                'django_help.templatetags.django_help_tags',
            ],
        },
    },
]
```

## Using Help Content in Templates

django-help provides several template tags to display help content:

```html
{% load django_help_tags %}

<!-- Display help button for the current path -->
{% django_help_current_path %}

<!-- Display help button for a specific category -->
{% django_help_category "getting-started" %}

<!-- Display help button for a specific article slug -->
{% django_help_slug "how-to-reset-password" %}

<!-- Display help button for a specific tag -->
{% django_help_tag "account-management" %}
```

These tags will render buttons that, when clicked, open a modal with the relevant help content.

## Customizing Templates

You can override default templates by creating your own in your project's template directory:

- `django_help/pages-index.html`: Main help page
- `django_help/pages-category.html`: Category listing page
- `django_help/fragments/modal_content.html`: Article display modal
- `django_help/markdownx/widget.html`: Markdown editor widget

## Creating and Managing Content

Use the Django admin interface to create and manage help content:

1. Navigate to the Django admin panel
2. Look for the "Django Help" section
3. Create categories, articles, and tags as needed

### Multi-language Content

When creating or editing articles, you'll see separate fields for each configured language. Fill in the content for each language as needed.

## Importing and Exporting Content

### Exporting Articles

1. In the Django admin, go to the DjangoHelp Articles section
2. Select articles to export
3. Choose the "Export selected articles to Markdown (.md) and/or ZIP" action
4. Download the resulting file(s)

### Importing Articles

1. Prepare Markdown files with YAML frontmatter for metadata
2. In the Django admin, go to the DjangoHelp Articles section
3. Click the "Upload" button
4. Choose a single .md file or a ZIP archive of multiple .md files
5. Submit the form to import the articles

## Extending Functionality

### Custom Models

Create custom models by extending the base models:

```python
from django.db import models

class CustomHelpArticle(models.Model):
    custom_field = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def custom_method(self):
        # Custom functionality
        pass

# Update DJANGO_HELP_CONFIG to use the custom model
DJANGO_HELP_CONFIG = {
    "BASE_MODEL": "myapp.models.CustomHelpArticle",
    # Other settings...
}
```

### Custom Authorization

Implement a custom authorization function:

```python
def custom_authorize_user(request, article):
    # Your custom authorization logic here
    return user_is_authorized

# Update DJANGO_HELP_CONFIG to use the custom function
DJANGO_HELP_CONFIG = {
    "AUTHORIZE_USER_TO_VIEW_ARTICLE": "myapp.utils.custom_authorize_user",
    # Other settings...
}
```
