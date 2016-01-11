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

from account.settings import ADMIN_LOGIN_URL
from account.utils import StaffPermissionRequiredMixin

from cms.models import Image

#########
# Image #
#########

class ImageList(StaffPermissionRequiredMixin, ListView):
    model = Image
    template_name = 'admin/cms/image_list.html'
    permission_required = 'cms.change_image'

    def get_queryset(self):
        return Image.objects.filter()

class ImageDelete(StaffPermissionRequiredMixin, DeleteView):
    model = Image
    permission_required = 'cms.delete_image'
    template_name = 'admin/cms/image_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, _('The image has been deleted.'))
        return reverse('cms-admin:image_list')
