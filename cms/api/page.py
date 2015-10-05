import json

from rest_framework import generics, permissions, filters
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.exceptions import PermissionDenied

from cms.serializers import PageTranslationSerializer
from cms.models import PageTranslation, Image

#
# Mixin for all translation views.
# Defines serializers, queryset and permissions
#

class TranslationMixin(object):
    def get_queryset(self):
        return PageTranslation.objects.filter()

    def get_serializer_class(self):
        return PageTranslationSerializer


class PageTranslationUpdate(TranslationMixin, generics.UpdateAPIView):

    lookup_field = 'id'
    parser_classes = (FormParser, MultiPartParser, )
    
    def perform_update(self, serializer):
        serializer.save()
        serializer.instance.parent.approval_needed = True
        serializer.instance.parent.save()

    def post(self, request, *args, **kwargs):

        if not request.user.has_perm('cms.change_pagetranslation'):
            raise PermissionDenied

        return self.partial_update(request, *args, **kwargs)

