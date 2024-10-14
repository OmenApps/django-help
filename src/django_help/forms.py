"""Forms for django_help."""

from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from django import forms
from django.conf import settings
from markdownx.fields import MarkdownxFormField
from markdownx.widgets import MarkdownxWidget
from translated_fields.utils import language_code_formfield_callback

from django_help.app_settings import EXTRA_LANGUAGES
from django_help.models import ArticleUpload
from django_help.models import DjangoHelpArticle
from django_help.models import RelevantPath


class RelevantPathForm(forms.ModelForm):
    """Form for creating RelevantPath instances."""

    class Meta:
        """Meta class for RelevantPathForm."""

        model = RelevantPath
        fields = ("path",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        # Use FormHelper to add form tags and set form attributes
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-8"


class DjangoHelpArticleForm(forms.ModelForm):
    """Form for creating and editing articles."""

    formfield_callback = language_code_formfield_callback

    class Meta:
        """Meta class for DjangoHelpArticleForm."""

        model = DjangoHelpArticle
        fields = (
            *DjangoHelpArticle.title.fields,
            *DjangoHelpArticle.subtitle.fields,
            "category",
            *DjangoHelpArticle.article_content.fields,
            "icon",
            "public",
            "highlighted",
            "intended_entity_type",
            "tags",
        )
        widgets = {
            f"article_content_{lang_code}": MarkdownxWidget(
                attrs={
                    "id": f"article_content_{lang_code}",
                    "class": "form-control",
                    "rows": 5,
                }
            )
            for lang_code, _ in settings.LANGUAGES
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create `title_{lang_code}`, `subtitle_{lang_code}`, and `article_content_{lang_code}` for each language.
        for lang_code, lang_name in settings.LANGUAGES:
            # For each below, if blank is not specified for the language in EXTRA_LANGUAGES, default to required=True.
            self.fields[f"title_{lang_code}"] = forms.CharField(
                label=f"Title ({lang_name})",
                required=EXTRA_LANGUAGES.get(lang_code, {}).get("blank", True),
            )
            self.fields[f"subtitle_{lang_code}"] = forms.CharField(
                label=f"Subtitle ({lang_name})",
                required=EXTRA_LANGUAGES.get(lang_code, {}).get("blank", True),
            )
            self.fields[f"article_content_{lang_code}"] = MarkdownxFormField(
                label=f"Article Content ({lang_name})",
                required=EXTRA_LANGUAGES.get(lang_code, {}).get("blank", True),
            )

        # tags should not be required
        self.fields["tags"].required = False

        self.helper = FormHelper()

        # Use FormHelper to add form tags and set form attributes
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-10"

        self.helper.layout = Layout(
            # Add a Div for the title, subtitle, and article_content fields for each language
            *[
                Div(
                    Field(f"title_{lang_code}", css_class="form-control"),
                    css_class="col-lg-12 mb-3",
                )
                for lang_code, lang_name in settings.LANGUAGES
            ],
            *[
                Div(
                    Field(f"subtitle_{lang_code}", css_class="form-control"),
                    css_class="col-lg-12 mb-3",
                )
                for lang_code, lang_name in settings.LANGUAGES
            ],
            Div(
                Field("category", css_class="form-control"),
                css_class="col-lg-12 mb-3",
            ),
            *[
                Div(
                    Field(f"article_content_{lang_code}", css_class="form-control"),
                    css_class="col-lg-12 mb-3",
                )
                for lang_code, lang_name in settings.LANGUAGES
            ],
            Div(
                Field("icon", css_class="form-control"),
                css_class="col-lg-12 mb-3",
            ),
            Div(
                Field("public", css_class="form-check-input"),
                css_class="col-lg-12 mb-3",
            ),
            Div(
                Field("highlighted", css_class="form-check-input"),
                css_class="col-lg-12 mb-3",
            ),
            Div(
                Field("intended_entity_type", css_class="form-control"),
                css_class="col-lg-12 mb-3",
            ),
            Div(
                PrependedText("tags", "#", placeholder="tags", css_class="form-control"),
                css_class="col-lg-12 mb-4",
            ),
        )


class ArticleUploadForm(forms.ModelForm):
    """Form for uploading articles in admin."""

    class Meta:
        """Meta class for ArticleUploadForm."""

        model = ArticleUpload
        fields = ["upload"]
