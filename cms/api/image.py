import json, urllib, re, os, io, decimal
from PIL import Image as PILImage

from django.conf import settings

from rest_framework import generics, permissions, filters
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from cms.serializers import ImageSerializer
from cms.models import Image


#
# Mixin for all company views.
# Defines serializers, queryset and permissions
#

class ImageMixin(object):

    def get_queryset(self):
        return Image.objects.filter()

    def get_serializer_class(self):
        return ImageSerializer


class ImageAdd(ImageMixin, generics.CreateAPIView):
    
    def perform_create(self, serializer):
        obj = serializer.save(
            image = self.request.data['image'], 
            name = self.request.data['image'].name)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.perform_create(serializer)

        instance = serializer.instance

        if hasattr(instance, '_width'):
            instance.display_width = instance._width

        # Save the size against the image
        instance.width = instance.read_size()[0]
        instance.height = instance.read_size()[1]

        instance.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers)

    def post(self, request, *args, **kwargs):

        if not request.user.has_perm('cms.add_image'):
            raise PermissionDenied

        return self.create(request, *args, **kwargs)


class ImageList(ImageMixin, generics.ListAPIView):
    pass


class ImageUpdate(ImageMixin, generics.UpdateAPIView):

    lookup_field = 'id'
    
    def post(self, request, *args, **kwargs):

        if not request.user.has_perm('cms.change_image'):
            raise PermissionDenied

        return self.partial_update(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, 
            data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        self.perform_update(serializer)

        instance = serializer.instance

        # Get image from image model instance
        image = instance.image

        if hasattr(instance, '_crop'):

            crop_values = instance._crop.split(',')

            # Crop values are percentages, so we need to convert them into
            # pixel values

            top = round(decimal.Decimal(crop_values[0]) * image.height)
            left = round(decimal.Decimal(crop_values[1]) * image.width)
            bottom = round(decimal.Decimal(crop_values[2]) * image.height)
            right = round(decimal.Decimal(crop_values[3]) * image.width)

            crop_box = (left, top, right, bottom)

            # Open the image with PIL
            im = PILImage.open(image.path)

            # Action the image rotation
            im = im.crop(crop_box)
            
            # Save the image
            im.save(image.path)

            # Save the size against the image
            instance.width = im.width
            instance.height = im.height

            
        elif hasattr(instance, '_direction'):
            
            angle = 270 if instance._direction == "CW" else 90
            
            # Open the image with PIL
            im = PILImage.open(image.path)

            # Action the image rotation
            im = im.rotate(angle)
            
            # Save the image
            im.save(image.path)

            # Save the size against the image
            instance.width = im.width
            instance.height = im.height

        else:
            # Save the size against the image
            instance.width = instance.read_size()[0]
            instance.height = instance.read_size()[1]


        if hasattr(instance, '_width'):
            instance.display_width = instance._width

        instance.save()

        return Response(serializer.data)
