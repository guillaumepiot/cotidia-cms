import json
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.conf import settings

from cotidia.account.utils import StaffPermissionRequiredMixin
from cotidia.cms.models import PageDataSet
from cotidia.cms.forms.dataset import (
    PageDataSetAddForm,
    PageDataSetUpdateForm)


###########################
# Page dataset management #
###########################

class PageDataSetList(StaffPermissionRequiredMixin, ListView):
    model = PageDataSet
    template_name = 'admin/cms/dataset/dataset_list.html'
    permission_required = 'cms.change_pagedataset'

    def get_queryset(self):
        return PageDataSet.objects.filter()

class PageDataSetDetail(StaffPermissionRequiredMixin, DetailView):
    model = PageDataSet
    template_name = 'admin/cms/dataset/dataset_detail.html'
    permission_required = 'cms.change_pagedataset'

class PageDataSetCreate(StaffPermissionRequiredMixin, CreateView):
    model = PageDataSet
    form_class = PageDataSetAddForm
    template_name = 'admin/cms/dataset/dataset_form.html'
    permission_required = 'cms.add_pagedataset'

    def get_success_url(self):
        messages.success(self.request, _('PageDataSet has been created.'))
        return reverse('cms-admin:pagedataset-detail', kwargs={'pk':self.object.id})

class PageDataSetUpdate(StaffPermissionRequiredMixin, UpdateView):
    model = PageDataSet
    form_class = PageDataSetUpdateForm
    template_name = 'admin/cms/dataset/dataset_form.html'
    permission_required = 'cms.change_pagedataset'

    def get_success_url(self):
        messages.success(self.request, _('PageDataSet details have been updated.'))
        return reverse('cms-admin:pagedataset-detail', kwargs={'pk':self.object.id})

class PageDataSetDelete(StaffPermissionRequiredMixin, DeleteView):
    model = PageDataSet
    permission_required = 'cms.delete_pagedataset'
    template_name = 'admin/cms/dataset/dataset_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, _('PageDataSet has been deleted.'))
        return reverse('cms-admin:pagedataset-list')
