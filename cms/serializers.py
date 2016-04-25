import json, time

from rest_framework import serializers

from cms.models import Image

class RegionSerializer(serializers.Serializer):

    regions = serializers.CharField(allow_null=True, required=False)
    images = serializers.CharField(allow_null=True, required=False)

    def to_representation(self, instance):
        ret = super(RegionSerializer, self).to_representation(instance)
        
        if ret.get('regions'):
            ret['regions'] = json.loads(ret['regions'])

        if ret.get('images'):
            ret['images'] = json.loads(ret['images'])

        return ret

class ImageSerializer(serializers.ModelSerializer):

    width = serializers.IntegerField(write_only=True, required=False)
    crop = serializers.CharField(write_only=True, required=False)
    direction = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Image
        fields = ('id',
                  'image',
                  'name',
                  'size',
                  'crop',
                  'direction',
                  'width',
                  'display_width',
                  )


    def to_representation(self, instance):
        ret = super(ImageSerializer, self).to_representation(instance)
        
        if ret['image']:
            
            # Modify the image URL by adding an _ignore param
            # This will force the browser to reload the image
            ret['image'] = "%s?_ignore=%s" % (ret['image'], time.time())

        ret['original_size'] = instance.original_size()
        
        return ret


    def create(self, validated_data):

        if validated_data.get('crop'):
            validated_data.pop('crop')

        if validated_data.get('direction'):
            validated_data.pop('direction')

        if validated_data.get('width'):
            width = validated_data.pop('width')
        else:
            width = None

        # Call default save
        instance = super(ImageSerializer, self).create(validated_data)

        if width:
            instance._width = width

        return instance


    def update(self, instance, validated_data):

        # Pop up the role, we only use it for the Profile object
        
        if validated_data.get('crop'):
            crop = validated_data.pop('crop')
        else:
            crop = None

        if validated_data.get('width'):
            width = validated_data.pop('width')
        else:
            width = None

        if validated_data.get('direction'):
            direction = validated_data.pop('direction')
        else:
            direction = None 

        # Call default save
        instance = super(ImageSerializer, self).update(instance, validated_data)


        if crop:
            instance._crop = crop

        if direction:
            instance._direction = direction

        if width:
            instance._width = width

        
        return instance