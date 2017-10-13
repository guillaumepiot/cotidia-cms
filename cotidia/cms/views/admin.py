import django_filters

from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from django.db import transaction

from cotidia.account.conf import settings
from cotidia.admin.views import AdminListView
from cotidia.admin.utils import StaffPermissionRequiredMixin

from cotidia.cms.conf import settings
from cotidia.cms.models import Page, PageTranslation
from cotidia.cms.forms.page import (
    PageAddForm,
    PageUpdateForm,
    PageURLForm,
    PageTitleForm
)
from cotidia.cms.forms.custom_form import TranslationForm


########
# Page #
########

class PageFilter(django_filters.FilterSet):
    display_title = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Title"
    )

    class Meta:
        model = Page
        fields = ['display_title']


class PageList(AdminListView):
    model = Page
    columns = (
        ('Title', 'display_title'),
        ('URL', 'get_absolute_url'),
        ('Status', 'status'),
        ('Show in menu', 'hide_from_nav'),
        ('Template', 'template_label'),
        ('Order', 'order'),
    )
    template_type = "fluid"
    filterset = PageFilter

    def get_queryset(self):
        return Page.objects.get_originals()


class PageDetail(StaffPermissionRequiredMixin, DetailView):
    model = Page
    template_name = 'admin/cms/page_detail.html'
    permission_required = 'cms.change_page'


class PageCreate(StaffPermissionRequiredMixin, CreateView):
    model = Page
    form_class = PageAddForm
    template_name = 'admin/cms/page_form.html'
    permission_required = 'cms.add_page'

    def get_success_url(self):
        messages.success(self.request, _('The page has been created.'))
        return reverse('cms-admin:page-list')


class PageUpdate(StaffPermissionRequiredMixin, UpdateView):
    model = Page
    form_class = PageUpdateForm
    template_name = 'admin/cms/page_form.html'
    permission_required = 'cms.change_page'

    def get_success_url(self):
        messages.success(self.request, _('The page details have been updated.'))
        return reverse('cms-admin:page-detail', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        response = super(PageUpdate, self).post(request, *args, **kwargs)
        if self.object.get_translations:
            self.object.approval_needed = True
            self.object.save()
        return response


class PageDelete(StaffPermissionRequiredMixin, DeleteView):
    model = Page
    permission_required = 'cms.delete_page'
    template_name = 'admin/cms/page_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, _('The page has been deleted.'))
        return reverse('cms-admin:page-list')


@login_required
@transaction.atomic()
def add_edit_translation(
        request,
        page_id,
        language_code,
        model_class=Page,
        translation_class=PageTranslation,
        translation_form_class=TranslationForm):

    if language_code not in [lang[0] for lang in settings.CMS_LANGUAGES]:
        raise ImproperlyConfigured('The language code "%s" is not included in the project settings.' % language_code)
    if not request.user.has_perm('cms.add_pagetranslation'):
        raise PermissionDenied
    page = get_object_or_404(model_class, id=page_id)

    translation = translation_class.objects.filter(
        parent=page,
        language_code=language_code
    ).first()

    initial = {
        'parent': page,
        'language_code': language_code
    }

    # Check is we are in revision mode
    # if recover_id:
    #     recover = True
    #     for version in reversion.get_unique_for_object(translation):
    #         if version.id == int(recover_id):
    #             # Set values from revision
    #             translation.title = version.field_dict['title']
    #             translation.slug = version.field_dict['slug']
    #             translation.content = version.field_dict['content']
    # else:
    #     recover = False

    if not translation:
        form = translation_form_class(page=page, initial=initial)
    else:
        if not request.user.has_perm('cmsbase.change_pagetranslation'):
            raise PermissionDenied

        form = translation_form_class(instance=translation, page=page, initial=initial)

    if request.method == 'POST':
        if not translation:
            form = translation_form_class(data=request.POST, files=request.FILES, page=page)
        else:
            form = translation_form_class(data=request.POST, files=request.FILES, instance=translation, page=page)
        if form.is_valid():
            translation = form.save()
            # reversion.set_user(request.user)

            # Notify the parent page that new content needs to be approved
            translation.parent.approval_needed = 1
            translation.parent.save()

            # if recover:
            #     messages.add_message(request, messages.SUCCESS, _('The content for "%s" has been recovered' % translation.title))
            # else:
            #     messages.add_message(request, messages.SUCCESS, _('The content for "%s" has been saved' % translation.title))
            messages.add_message(request, messages.SUCCESS, _('The meta data for "%s" has been saved' % translation.title))
            return HttpResponseRedirect(reverse('cms-admin:page-detail', kwargs={'pk':page.id}))

    print("form", form)

    template = 'admin/cms/page_metadata_form.html'

    context = {
        'form': form,
        'page': page,
        'translation': translation,
    }
    return render(request, template, context)


##############
# Publishing #
##############

@permission_required('cms.publish_page', settings.ACCOUNT_ADMIN_LOGIN_URL)
def PagePublish(request, page_id):

    page = get_object_or_404(Page, id=page_id)

    if request.method == 'POST':
        if page.get_translations():

            page.approval_needed = False
            page.published = True
            page.save()
            page.publish_version()
            page.publish_translations()

            messages.success(request, _('The page has been published.'))

        return HttpResponseRedirect(
            reverse('cms-admin:page-detail', kwargs={'pk': page.id}))

    template = 'admin/cms/page_publish_form.html'

    return render(request, template, {'page': page})


@permission_required('cms.publish_page', settings.ACCOUNT_ADMIN_LOGIN_URL)
def PageUnpublish(request, page_id):

    page = get_object_or_404(Page, id=page_id)

    if request.method == 'POST':
        if page.get_translations():

            page.approval_needed = False
            page.published = False
            page.save()
            page.unpublish_version()

            messages.success(request, _('The page has been unpublished.'))

        return HttpResponseRedirect(
            reverse('cms-admin:page-detail', kwargs={'pk': page.id}))

    template = 'admin/cms/page_unpublish_form.html'

    return render(request, template, {'page': page})


###########
# Content #
###########

@permission_required('cms.add_pagetranslation', settings.ACCOUNT_ADMIN_LOGIN_URL)
def PageURLCreate(request, page_id, lang):

    page = get_object_or_404(Page, id=page_id)

    form = PageURLForm()

    if request.method == 'POST':
        form = PageURLForm(request.POST)

        if form.is_valid():
            translation = form.save(commit=False)
            translation.parent = page
            translation.language_code = lang
            translation.save()

            page.approval_needed = True
            page.save()

            messages.success(request, _('The page URL has been saved.'))

            return HttpResponseRedirect(
                reverse('cms-admin:page-detail', kwargs={'pk': page.id}))

    template = 'admin/cms/page_url_form.html'

    return render(request, template, {'form': form, 'page': page})


@permission_required('cms.change_pagetranslation', settings.ACCOUNT_ADMIN_LOGIN_URL)
def PageURLUpdate(request, page_id, lang, trans_id):

    page = get_object_or_404(Page, id=page_id)
    translation = get_object_or_404(PageTranslation, id=trans_id)

    form = PageURLForm(instance=translation)

    if request.method == 'POST':
        form = PageURLForm(request.POST, instance=translation)

        if form.is_valid():
            translation = form.save(commit=False)
            translation.parent = page
            translation.language_code = lang
            translation.save()

            page.approval_needed = True
            page.save()

            messages.success(request, _('The page URL has been saved.'))

            return HttpResponseRedirect(
                reverse('cms-admin:page-detail', kwargs={'pk': page.id}))

    template = 'admin/cms/page_url_form.html'

    return render(
        request,
        template,
        {
            'form': form,
            'page': page,
            'translation': translation
        }
    )


#
# Manage the page title for a language
#
@permission_required('cms.change_page', settings.ACCOUNT_ADMIN_LOGIN_URL)
def PageTitleUpdate(request, page_id, lang, trans_id=None):

    page = get_object_or_404(Page, id=page_id)
    if trans_id:
        translation = get_object_or_404(PageTranslation, id=trans_id)
        form = PageTitleForm(instance=translation)
    else:
        translation = None
        form = PageTitleForm()

    if request.method == 'POST':

        if translation:
            form = PageTitleForm(instance=translation, data=request.POST)
        else:
            form = PageTitleForm(data=request.POST)

        if form.is_valid():

            translation = form.save(commit=False)
            translation.parent = page
            translation.language_code = lang
            if not translation.slug:
                translation.slug = slugify(translation.title.lower())
            translation.save()

            page.approval_needed = True
            page.save()

            messages.success(request, _('The page title has been saved.'))

            return HttpResponseRedirect(
                reverse('cms-admin:page-detail', kwargs={'pk': page.id}))

    template = 'admin/cms/page_title_form.html'

    return render(request, template, {'form': form, 'page': page})

