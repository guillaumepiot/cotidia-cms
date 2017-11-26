from django.utils.translation import ugettext_lazy as _

from betterforms.forms import BetterModelForm

from cotidia.cms.models import PageTranslation


class PageTitleAddForm(BetterModelForm):

    class Meta:
        model = PageTranslation
        fields = [
            'title'
        ]
        fieldsets = (
            ('info', {
                'fields': (
                    'title',
                ),
                'legend': 'Page title'
            }),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].help_text = _(
            "The title will be used for navigation items."
        )
        self.fields["title"].label = _(
            "Choose a title"
        )


class PageTitleUpdateForm(BetterModelForm):

    class Meta:
        model = PageTranslation
        fields = [
            'title'
        ]
        fieldsets = (
            ('info', {
                'fields': (
                    'title',
                ),
                'legend': 'Page title'
            }),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].help_text = _(
            "The title will be used for navigation items."
        )
        self.fields["title"].label = _(
            "New title"
        )
