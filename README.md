# django-help

[![PyPI](https://img.shields.io/pypi/v/django-help.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/django-help.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/django-help)][pypi status]
[![License](https://img.shields.io/pypi/l/django-help)][license]

[![Read the documentation at https://django-help.readthedocs.io/](https://img.shields.io/readthedocs/django-help/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/OmenApps/django-help/actions/workflows/tests.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/jacklinke/django-help/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/django-help/
[read the docs]: https://django-help.readthedocs.io/
[tests]: https://github.com/OmenApps/django-help/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/jacklinke/django-help
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Overview

> [!WARNING]
> This project is under active development and not yet ready for production use.

django-help is a powerful and flexible Django package that provides a multilingual knowledge base and help system for Django applications. Its standout features include multi-language support and seamless import/export functionality, making it an ideal solution for creating and managing help content across different languages and projects.

## Key Features

1. **Multi-Language Support**:
   - Create and manage help content in multiple languages
   - Easily translate articles, categories, and tags
   - Language-specific content display based on user preferences or settings

2. **Import/Export Functionality**:
   - Import single articles or bulk import multiple articles
   - Export individual articles or entire knowledge bases
   - Support for Markdown format with YAML frontmatter for metadata

3. **Article Management**:
   - Create and edit help articles using Markdown for rich text formatting
   - Organize content with categories and tags
   - Set article visibility and highlight important content

4. **Contextual Help**:
   - Associate articles with specific URL paths for context-sensitive help
   - Display relevant content based on the user's current location in the application

5. **Search Functionality**:
   - Full-text search across all articles, titles, and tags in multiple languages
   - Customizable search results ranking and filtering

6. **User Interface**:
   - Responsive design for optimal viewing on various devices
   - Customizable templates for seamless integration with your application's look and feel
   - Modal view support for displaying help content without page navigation

7. **Admin Interface**:
   - User-friendly Django admin integration for content management
   - Bulk actions for efficient article and category management

8. **Extensibility**:
   - Customizable base models and querysets for tailored functionality
   - Hooks for adding custom authorization logic

## Requirements

- Python 3.10 or higher
- Django 4.2 or higher
- Additional dependencies:
  - django-markdownx 4.0+: For Markdown editing and rendering
  - django-translated-fields 0.13+: For multi-language support
  - django-taggit 6.1+: For tagging functionality
  - python-frontmatter 1.1+: For parsing Markdown files with metadata
  - django-crispy-forms 2.3+: For enhanced form rendering
  - crispy-bootstrap5 2024.2+: For Bootstrap 5 styling in crispy forms

## Installation

Install django-help using pip:

```console
$ pip install django-help
```

## Quick Start Guide

1. Add required apps to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_help',
    'markdownx',
    'taggit',
    'crispy_forms',
    'crispy_bootstrap5',
]
```

And add the django_help_tags to your `TEMPLATES` builtins:

```python
TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'builtins': [
                'django_help.templatetags.django_help_tags',
            ],
        },
    },
]
```

2. Include django-help URLs in your project's `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    ...
    path('help/', include('django_help.urls')),
]
```

3. Run migrations to create necessary database tables:

```console
$ python manage.py migrate django_help
```

4. Configure your static files settings to include django-help static files:

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    ...
    ('django_help', 'path/to/your/django_help/static'),
]
```

5. Start creating help content through the Django admin interface.

## Multi-Language Support

django-help uses django-translated-fields to provide robust multi-language support for your help content.

### Configuration

1. Define your project's languages in your project's settings, per Django's [translations documentation]:

```python
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    # Add languages as needed
]
```

2. Configure additional language settings in `DJANGO_HELP_CONFIG`:

This configuration allows you to specify which languages are available for translation in django-help. To make translations for each language required or optional in models and forms, set the `blank` key for each language:

```python
DJANGO_HELP_CONFIG = {
    "EXTRA_LANGUAGES": {
        "es": {"blank": False},  # Spanish translations are required
        "fr": {"blank": True},   # French translations are optional
    },
    # Other settings...
}
```

### Creating Multi-Language Content

When creating or editing articles in the admin interface, you'll see separate fields for each configured language:

- Title (English)
- Title (Spanish)
- Title (French)
- Content (English)
- Content (Spanish)
- Content (French)

Fill in the content for each language as needed. If a language is set to `"blank": True` in the configuration, it's optional.

### Displaying Multi-Language Content

django-help automatically displays content in the user's preferred language based on Django's language settings. You can also manually control the displayed language:

```python
from django.utils.translation import activate

activate('es')  # Switch to Spanish
# Your view logic here
```

### Display help content in your templates:

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

## Import/Export Functionality

django-help provides powerful import and export capabilities for managing your help content.

### Exporting Articles

1. In the Django admin interface, go to the DjangoHelp Articles section.
2. Select the articles you want to export.
3. Choose the "Export selected articles to Markdown (.md) and/or ZIP" action.
4. If exporting a single article, you'll get a .md file. For multiple articles, you'll receive a ZIP archive.

### Importing Articles

You can import articles individually or in bulk:

1. Prepare your Markdown files with YAML frontmatter for metadata:

```markdown
---
title: How to Reset Your Password
slug: reset-password
category: Account Management
tags: password, account, security
---

# How to Reset Your Password

1. Go to the login page
2. Click on "Forgot Password"
3. ...
```

2. In the Django admin interface, go to the DjangoHelp Articles section.
3. Click on the "Upload" button.
4. Choose either a single .md file or a ZIP archive containing multiple .md files.
5. Submit the form to import the articles.

### Bulk Import/Export

__(This feature is planned for a future release.)__

For large-scale import or export operations, you can use management commands:

```console
# Export all articles
$ python manage.py export_help_articles

# Import articles from a directory
$ python manage.py import_help_articles /path/to/article/directory
```

### Multi-Language Import/Export

When exporting, each article's file will contain content for all configured languages:

```markdown
---
title_en: How to Reset Your Password
title_es: Cómo Restablecer tu Contraseña
title_fr: Comment Réinitialiser Votre Mot de Passe
slug: reset-password
category: Account Management
tags: password, account, security
---

# English Content

How to reset your password...

# Contenido en Español

Cómo restablecer tu contraseña...

# Contenu en Français

Comment réinitialiser votre mot de passe...
```

When importing, the system will automatically detect and populate the appropriate language fields based on the frontmatter and content structure.

## Advanced Usage

### Customizing Templates

Override default templates by creating your own in your project's template directory:

- `django_help/pages-index.html`: Main help page
- `django_help/pages-category.html`: Category listing page
- `django_help/fragments/modal_content.html`: Article display modal
- `django_help/markdownx/widget.html`: Markdown editor widget

### Extending Models

Extend base models for custom functionality:

```python
from django.db import models

class CustomHelpArticle(models.Model):
    custom_field = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def custom_method(self):
        # Custom functionality
        pass
```

Update your `DJANGO_HELP_CONFIG` to use the custom model:

```python
DJANGO_HELP_CONFIG = {
    "BASE_MODEL": "myapp.models.CustomHelpArticle",
    # Other settings...
}
```

## Contributing

We welcome contributions to django-help! Please see our [Contributor Guide] for details on how to get started, our code of conduct, and the process for submitting pull requests.

## License

django-help is distributed under the terms of the [MIT license][license]. This project is free and open-source software.

## Support and Issues

If you encounter any problems or have questions, please [file an issue] on our GitHub repository. For general discussions or questions, you can use the Discussions tab on GitHub.

## Credits

This project was generated from [@OmenApps]'s [Cookiecutter Django Package] template.

[@omenapps]: https://github.com/OmenApps
[pypi]: https://pypi.org/
[cookiecutter django package]: https://github.com/OmenApps/cookiecutter-django-package
[file an issue]: https://github.com/OmenApps/django-help/issues
[pip]: https://pip.pypa.io/
[license]: https://github.com/OmenApps/django-help/blob/main/LICENSE
[contributor guide]: https://github.com/OmenApps/django-help/blob/main/CONTRIBUTING.md
[command-line reference]: https://django-help.readthedocs.io/en/latest/usage.html
[translations documentation]: https://docs.djangoproject.com/en/stable/topics/i18n/translation/
