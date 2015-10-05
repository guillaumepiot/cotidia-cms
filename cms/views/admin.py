from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext  
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect 
from django.utils.text import slugify

from cms.settings import ADMIN_LOGIN_URL
from cms.models import Page, PageTranslation
from cms.forms import PageAddForm, PageURLForm, PageTitleForm
from cms.utils import StaffPermissionRequiredMixin

########
# Page #
########

class PageList(StaffPermissionRequiredMixin, ListView):
    model = Page
    template_name = 'admin/cms/page_list.html'
    permission_required = 'cms.change_page'

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
        return reverse('cms-admin:page_list')

class PageUpdate(StaffPermissionRequiredMixin, UpdateView):
    model = Page
    form_class = PageAddForm
    template_name = 'admin/cms/page_form.html'
    permission_required = 'cms.change_page'

    def get_success_url(self):
        messages.success(self.request, _('The page details have been updated.'))
        return reverse('cms-admin:page_detail', kwargs={'pk':self.object.id})

    def post(self, request, *args, **kwargs):
        response = super(PageUpdate, self).post(request, *args, **kwargs)
        if self.object.get_translations:
            self.object.approval_needed = True
            self.object.save()
        return response

class PageDelete(StaffPermissionRequiredMixin, DeleteView):
    model = Page
    success_url = reverse_lazy('cms-admin:page_list')
    permission_required = 'cms.delete_page'
    template_name = 'admin/cms/page_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, _('The page has been deleted.'))
        return reverse('cms-admin:page_list')


##############
# Publishing #
##############

@permission_required('cms.publish_page', ADMIN_LOGIN_URL)
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
            reverse('cms-admin:page_detail', kwargs={'pk': page.id}))
    
    template = 'admin/cms/page_publish_form.html'

    return render_to_response(template, {'page':page},
        context_instance=RequestContext(request))

@permission_required('cms.publish_page', ADMIN_LOGIN_URL)
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
            reverse('cms-admin:page_detail', kwargs={'pk': page.id}))
    
    template = 'admin/cms/page_unpublish_form.html'

    return render_to_response(template, {'page':page},
        context_instance=RequestContext(request))

###########
# Content #
###########

@permission_required('cms.add_pagetranslation', ADMIN_LOGIN_URL)
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
                reverse('cms-admin:page_detail', kwargs={'pk': page.id}))
    
    template = 'admin/cms/page_url_form.html'

    return render_to_response(template, {'form':form, 'page':page},
        context_instance=RequestContext(request))

@permission_required('cms.change_pagetranslation', ADMIN_LOGIN_URL)
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
                reverse('cms-admin:page_detail', kwargs={'pk': page.id}))
    
    template = 'admin/cms/page_url_form.html'

    return render_to_response(template, {
        'form':form, 'page':page, 'translation':translation},
        context_instance=RequestContext(request))

#
# Manage the page title for a language
#
@permission_required('cms.change_page', ADMIN_LOGIN_URL)
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
                reverse('cms-admin:page_detail', kwargs={'pk': page.id}))
    
    template = 'admin/cms/page_title_form.html'

    return render_to_response(template, {'form':form, 'page':page},
        context_instance=RequestContext(request))
