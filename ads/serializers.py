from rest_framework import serializers
from rest_framework.fields import ReadOnlyField

from .models import Ad



class AdSerializer(serializers.ModelSerializer):
    publisher = ReadOnlyField(source='publisher.username')
    class Meta:
        model = Ad
        fields = '__all__'
        read_only_fields = ['id', 'is_public', 'date_added']
        extra_kwargs = {'image':{'required':False}}
