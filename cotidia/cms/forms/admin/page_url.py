import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from betterforms.forms import BetterModelForm

from cotidia.cms.models import PageTranslation


class PageURLForm(BetterModelForm):

    class Meta:
        model = PageTranslation
        fields = [
            'slug'
        ]
        fieldsets = (
            ('slug', {
                'fields': (
                    'slug',
                ),
                'legend': 'Page URL'
            }),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].help_text = _(
            "The URL should only contain lowercase letters, "
            "numbers and dashes (-)."
        )
        self.fields["slug"].widget = forms.TextInput(attrs={
            'onKeyUp': 'updateSlug(this)'
        })

    def clean_slug(self):

        slug = self.cleaned_data['slug']

        # Trim spaces
        slug = slug.strip()

        slug_pattern = re.compile("^([a-z0-9\-]+)$")

        if not slug_pattern.match(slug):
            raise forms.ValidationError(
                _(
                    "The URL is not valid "
                    "because it contains unallowed characters. "
                    "Only lowercase letters, numbers and dashes are accepted."
                )
            )

        pages = [page.slug for page in PageTranslation.objects.all()]

        error_message = _('The unique page identifier must be unique')

        if self.instance and slug in pages \
                and slug != self.instance.slug and slug != '':
            raise forms.ValidationError(error_message)

        elif not self.instance and slug in pages and slug != '':
            raise forms.ValidationError(error_message)

        else:
            return slug
