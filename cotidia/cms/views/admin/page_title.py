from django.contrib import messages
from django.utils.text import slugify

from cotidia.admin.views import (
    AdminChildCreateView,
    AdminChildUpdateView
)

from cotidia.cms.models import Page, PageTranslation
from cotidia.cms.forms.admin.page_title import (
    PageTitleAddForm,
    PageTitleUpdateForm,
)


class PageTitleCreate(AdminChildCreateView):
    model = PageTranslation
    form_class = PageTitleAddForm
    parent_model = Page
    parent_model_foreign_key = "parent"

    def get_lang(self, *args, **kwargs):
        lang = kwargs["lang"]
        return lang

    def get(self, *args, **kwargs):
        self.lang = self.get_lang(*args, **kwargs)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.lang = self.get_lang(*args, **kwargs)
        return super().post(*args, **kwargs)

    def get_success_url(self):
        messages.success(
            self.request,
            'The page title has been saved.'.format(self.model._meta.verbose_name)
        )
        return self.build_success_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        self.object.language_code = self.lang
        if not self.object.slug:
            self.object.slug = slugify(self.object.title.lower())
        self.object.save()

        self.parent.approval_needed = True
        self.parent.save()

        return response


class PageTitleUpdate(AdminChildUpdateView):
    model = PageTranslation
    form_class = PageTitleUpdateForm
    parent_model = Page
    parent_model_foreign_key = "parent"
    template_name = 'admin/cms/page/child_form.html'

    def get_lang(self, *args, **kwargs):
        lang = kwargs["lang"]
        return lang

    def get(self, *args, **kwargs):
        self.lang = self.get_lang(*args, **kwargs)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.lang = self.get_lang(*args, **kwargs)
        return super().post(*args, **kwargs)

    def get_success_url(self):
        messages.success(
            self.request,
            'The page title has been updated.'.format(self.model._meta.verbose_name)
        )
        return self.build_success_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        self.object.language_code = self.lang
        if not self.object.slug:
            self.object.slug = slugify(self.object.title.lower())
        self.object.save()

        self.parent.approval_needed = True
        self.parent.save()

        return response
