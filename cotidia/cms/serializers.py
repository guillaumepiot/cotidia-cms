import json

from rest_framework import serializers


class RegionSerializer(serializers.Serializer):

    regions = serializers.CharField(allow_null=True, required=False)
    images = serializers.CharField(allow_null=True, required=False)

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if ret.get('regions'):
            ret['regions'] = json.loads(ret['regions'])

        if ret.get('images'):
            ret['images'] = json.loads(ret['images'])

        return ret
