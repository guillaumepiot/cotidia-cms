from django import forms
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from mptt.forms import TreeNodeChoiceField
from betterforms.forms import BetterModelForm

from cotidia.cms.models import Page, PageDataSet
from cotidia.cms.conf import settings


class PageAddForm(BetterModelForm):

    template = forms.ChoiceField(
        help_text=_(
            "The template defines the layout of page, as well as the "
            "editable areas."
        ),
        choices=settings.CMS_PAGE_TEMPLATES
    )

    class Meta:
        model = Page
        fields = ['display_title', 'template', 'parent', 'home', 'hide_from_nav']
        fieldsets = (
            ('info', {
                'fields': (
                    'display_title',
                    'template',
                    'parent',
                ),
                'legend': 'Page information'
            }),
            ('options', {
                'fields': (
                    'home',
                    'hide_from_nav',
                ),
                'legend': 'Options'
            }),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["display_title"].help_text = _(
            "The display title is only used to represent the page "
            "within the CMS. This value should not be used for the title "
            "displayed on the web page."
        )
        self.fields["home"].help_text = _(
            "Mark this page as home page"
        )
        self.fields["hide_from_nav"].help_text = _(
            "Hide this page from the main menu"
        )
        self.fields["parent"].queryset = Page.objects.get_originals()
        self.fields["parent"].help_text = _("Leave blank if this a top level page.")

    def clean_home(self):
        home = self.cleaned_data['home']

        if home:
            err_message = _("There is already another page set as home.")

            # Check if other pages are already home excluded the current
            # edited page
            if self.instance:
                if self.Meta.model.objects.filter(
                    published_from=None,
                    home=True
                ).exclude(id=self.instance.id):
                    raise forms.ValidationError(err_message)
            # Check if other pages are already home excluded
            else:
                if self.Meta.model.objects.filter(
                    published_from=None, home=True
                ):
                    raise forms.ValidationError(err_message)

        return home


class PageUpdateForm(PageAddForm):

    slug = forms.CharField(
        label='Unique page identifier',
        help_text=_("A unique identifier to allow retrieving a page"),
        required=False
    )

    dataset = forms.ModelChoiceField(
        queryset=PageDataSet.objects.all(),
        required=False
    )

    redirect_to = TreeNodeChoiceField(
        label="Redirect to an internal page",
        queryset=Page.objects.get_published_originals(),
        help_text=_('Redirect this page to another page in the system'),
        required=False
    )

    redirect_to_url = forms.CharField(
        label="Redirect to a url",
        help_text=_("Enter the full web address."),
        required=False
    )

    class Meta:
        model = Page
        fields = [
            'home',
            'display_title',
            'template',
            'parent',
            'hide_from_nav',
            'dataset',
            'redirect_to',
            'redirect_to_url',
            'slug'
        ]
        fieldsets = (
            ('info', {
                'fields': (
                    'display_title',
                    'template',
                    'parent',
                ),
                'legend': 'Page information'
            }),
            ('dataset', {
                'fields': (
                    'dataset',
                ),
                'legend': 'Dataset'
            }),
            ('redirect', {
                'fields': (
                    'redirect_to',
                    'redirect_to_url',
                ),
                'legend': 'Redirect'
            }),

            ('options', {
                'fields': (
                    'home',
                    'hide_from_nav',
                    'slug'
                ),
                'legend': 'Options'
            }),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dataset_url = reverse("cms-admin:pagedataset-list")
        self.fields["dataset"].help_text = (
            "Choose a dataset to add more custom data to the page. "
            "<a href=\"{}\">Manage datasets</a>"
        ).format(dataset_url)




