import io
import decimal

from PIL import Image as PILImage

from django.core.files.storage import default_storage

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from cotidia.cms.serializers import ImageSerializer
from cotidia.cms.models import Image


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
        serializer.save(
            image=self.request.data['image'],
            name=self.request.data['image'].name)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        instance = serializer.instance

        # Save the size against the image
        instance.width = instance.read_size()[0]
        instance.height = instance.read_size()[1]

        if hasattr(instance, '_width'):
            instance.display_width = instance._width
            instance.display_height = instance.calculate_display_height()

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
        serializer = self.get_serializer(
            instance,
            data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        instance = serializer.instance

        # Get image from image model instance
        image = instance.image

        if len(image.name.split('.')) > 1:
            file_ext = image.name.split('.')[-1]
            if file_ext == 'jpg':
                file_ext = "JPEG"
        else:
            file_ext = "JPEG"

        if file_ext not in ['PNG', 'JPEG', 'GIF']:
            file_ext = "JPEG"

        try:
            # Open the image with PIL locally
            im = PILImage.open(image.path)
            output = None
            img_file = None
        except:
            # Try open with django storage, in case of external hosting (S3)
            img_file = default_storage.open(image.name, 'rw')
            im = io.BytesIO(img_file.read())
            im = PILImage.open(im)
            output = io.BytesIO()

        if hasattr(instance, '_crop'):

            crop_values = instance._crop.split(',')

            # Crop values are percentages, so we need to convert them into
            # pixel values

            top = round(decimal.Decimal(crop_values[0]) * image.height)
            left = round(decimal.Decimal(crop_values[1]) * image.width)
            bottom = round(decimal.Decimal(crop_values[2]) * image.height)
            right = round(decimal.Decimal(crop_values[3]) * image.width)

            crop_box = (int(left), int(top), int(right), int(bottom))

            # Action the image rotation
            im = im.crop(crop_box)

            if output:
                # Save cropped image to buffer
                im.save(output, file_ext.upper())
                # Save new image to storage
                img_file.write(output.getvalue())
                img_file.close()
            else:
                im.save(image.path)

            # Save the size against the image
            instance.width = im.width
            instance.height = im.height

        elif hasattr(instance, '_direction'):

            angle = 270 if instance._direction == "CW" else 90

            # Action the image rotation
            im = im.rotate(angle)

            if output:
                # Save rotated image to buffer
                im.save(output, file_ext.upper())
                # Save new image to storage
                img_file.write(output.getvalue())
                img_file.close()
            else:
                im.save(image.path)

            # Save the size against the image
            # Invert the width and height since we are rotating either 90 or
            # 270 degrees
            instance.width = im.height
            instance.height = im.width

            original_display_width = instance.display_width
            original_display_height = instance.display_height

            instance.display_width = original_display_height
            instance.display_height = original_display_width

        else:
            # Save the size against the image
            instance.width = instance.read_size()[0]
            instance.height = instance.read_size()[1]

        if hasattr(instance, '_width'):
            instance.display_width = instance._width
            instance.display_height = instance.calculate_display_height()

        instance.save()

        return Response(serializer.data)
