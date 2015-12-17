import json, time

from rest_framework import serializers

from cms.models import PageTranslation, Image

class PageTranslationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PageTranslation
        fields = ('id', 'regions', 'images')

    def to_representation(self, instance):
        ret = super(PageTranslationSerializer, self).to_representation(instance)
        
        if ret['regions']:
            ret['regions'] = json.loads(ret['regions'])

        return ret

    def update(self, instance, validated_data):

        if instance.regions:
            current_data = dict(json.loads(instance.regions))
        else:
            current_data = None
            
        if not current_data:
            current_data = {}

        if validated_data.get('regions'):
            new_data = dict(json.loads(validated_data.get('regions')))
            for key, value in new_data.items():
                current_data[key] = value

            validated_data['regions'] = json.dumps(current_data)

        instance = super(PageTranslationSerializer, self).update(instance, validated_data)

        return instance

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