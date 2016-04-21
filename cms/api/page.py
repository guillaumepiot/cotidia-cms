import json

from rest_framework import generics, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.exceptions import PermissionDenied
from rest_framework import status

from django.apps import apps

from cms.serializers import RegionSerializer
from cms.models import PageTranslation, Image

#
# Define a view for region handling
#
class RegionUpdate(APIView):

    parser_classes = (FormParser, MultiPartParser, )
    serializer_class = RegionSerializer
    
    # def perform_update(self, serializer):
    #     serializer.save()
    #     serializer.instance.parent.approval_needed = True
    #     serializer.instance.parent.save()

    def post(self, request, *args, **kwargs):

        #
        # Retrieve the model path from the POST request
        #
        model_str = request.data.get('model')
        if not model_str or model_str == "null":
            return Response({'message': "Please specify the model name"}, 
                status=status.HTTP_400_BAD_REQUEST)
        
        #
        # Define permission string
        #
        app_name, model_name = model_str.split('.')
        perm = "%s.change_%s" % (app_name, model_name.lower())

        if not request.user.has_perm(perm):
            raise PermissionDenied

        #
        # Retrieve the model class
        #
        ContentModel = apps.get_model(app_name, model_name)
        # Try to retrieve the current object for that model
        try:
            content_model = ContentModel.objects.get(id=kwargs['id'])
        except ContentModel.DoesNotExist:
            return Response({'message': "The model instance was not found"}, 
                status=status.HTTP_400_BAD_REQUEST)
        #
        # Instantiate serializer
        #
        serializer = RegionSerializer(data=request.data)
        if serializer.is_valid():
            regions = serializer.data['regions']
            images = serializer.data['images']
            
            #
            # Combine the existing regions with the submitted regions
            #
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

