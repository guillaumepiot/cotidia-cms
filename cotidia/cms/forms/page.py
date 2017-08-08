import re
from django import forms
from django.utils.translation import ugettext_lazy as _
from mptt.forms import TreeNodeChoiceField

from cotidia.cms.models import Page, PageTranslation, PageDataSet
from cotidia.cms.settings import CMS_PAGE_TEMPLATES


class PageAddForm(forms.ModelForm):

    home = forms.BooleanField(
        label=_("<span class=\"fa fa-home\"></span> Home page"),
        required=False)

    display_title = forms.CharField(
        label='',
        help_text=_(
            "The display title is only used to represent the page "
            "within the CMS. This value should not be used for the title "
            "displayed on the web page."
        ),
        widget=forms.TextInput(attrs={'class': 'form__text'})
    )

    template = forms.ChoiceField(
        label='',
        help_text=_(
            "The template defines the layout of page, as well as the "
            "editable areas."
        ),
        choices=CMS_PAGE_TEMPLATES,
        widget=forms.Select(attrs={'class': 'form__select'})
    )

    parent = forms.ModelChoiceField(
        label='',
        help_text=("Leave blank if this a top level page."),
        queryset=Page.objects.get_originals(),
        widget=forms.Select(attrs={'class': 'form__select'}),
        required=False
    )

    hide_from_nav = forms.BooleanField(
        label=_("Hide from menu"),
        help_text=_(
            "Check this box if you want to hide this page "
            "from the main menu"
        ),
        widget=forms.CheckboxInput(attrs={'class': 'form__checkbox'}),
        required=False
    )

    class Meta:
        model = Page
        fields = [
            'home',
            'display_title',
            'template',
            'parent',
            'hide_from_nav'
        ]

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
        label='',
        help_text=_("A unique identifier to allow retrieving a page"),
        widget=forms.TextInput(attrs={'class': 'form__text'}),
        required=False
    )

    dataset = forms.ModelChoiceField(
        label="",
        queryset=PageDataSet.objects.all(),
        widget=forms.Select(attrs={'class': 'form__select'}),
        required=False
    )

    redirect_to = TreeNodeChoiceField(
        label='',
        queryset=Page.objects.get_published_originals(),
        help_text=_('Redirect this page to another page in the system'),
        widget=forms.Select(attrs={'class': 'form__select'}),
        required=False)

    redirect_to_url = forms.CharField(
        label='',
        help_text=_("Enter the full web address."),
        widget=forms.TextInput(attrs={'class': 'form__text'}),
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


class PageURLForm(forms.ModelForm):

    slug = forms.CharField(
        label='',
        help_text=_(
            "The URL should only contain lowercase letters, "
            "numbers and dashes (-)."
        ),
        widget=forms.TextInput(attrs={
            'class': 'form__text',
            'onKeyUp': 'updateSlug(this)'
        })
    )

    class Meta:
        model = PageTranslation
        fields = [
            'slug'
        ]

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


class PageTitleForm(forms.ModelForm):

    title = forms.CharField(
        label='',
        help_text=_("The title will be used for navigation items."),
        widget=forms.TextInput(attrs={'class': 'form__text'})
    )

    class Meta:
        model = PageTranslation
        fields = [
            'title'
        ]
