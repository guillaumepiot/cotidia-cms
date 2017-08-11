import json

from django.contrib.contenttypes.models import ContentType

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.exceptions import PermissionDenied
from rest_framework import status

from django.apps import apps

from cotidia.cms.serializers import RegionSerializer


class RegionUpdate(APIView):
    """Define a view for region handling."""

    parser_classes = (FormParser, MultiPartParser, )
    serializer_class = RegionSerializer

    def post(self, request, *args, **kwargs):

        # Retrieve the model path from the POST request
        content_type_id = request.data.get('content_type_id')
        if not content_type_id or content_type_id == "null":
            return Response(
                {'message': "Please specify the content type id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Define permission string
        content_type = ContentType.objects.get(id=content_type_id)
        perm = "{}.change_{}".format(
            content_type.app_label,
            content_type.model
        )

        if not request.user.has_perm(perm):
            raise PermissionDenied

        # Retrieve the model class
        content_model = apps.get_model(
            content_type.app_label,
            content_type.model
        )
        # Try to retrieve the current object for that model
        try:
            content_model = content_model.objects.get(id=kwargs['id'])
        except content_model.DoesNotExist:
            return Response(
                {'message': "The model instance was not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Instantiate serializer
        serializer = RegionSerializer(data=request.data)
        if serializer.is_valid():
            regions = serializer.data.get('regions')
            images = serializer.data.get('images')

            # Combine the existing regions with the submitted regions
            if content_model.regions:
                current_data = dict(json.loads(content_model.regions))
            else:
                current_data = None

            if not current_data:
                current_data = {}

            if regions:
                for key, value in regions.items():
                    current_data[key] = value

            if images:
                content_model.images = json.dumps(images)

            content_model.regions = json.dumps(current_data)
            content_model.save()

            # Mark the parent as approval needed
            content_model.parent.approval_needed = True
            content_model.parent.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
