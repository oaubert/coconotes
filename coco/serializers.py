from rest_framework import serializers
from .models import Course, Video
from django.contrib.auth.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ( 'username', 'first_name', 'last_name' )

class VideoSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False)
    contributor = UserSerializer(many=False)
    class Meta:
        model = Video
        fields = ('id',
                  'creator', 'created', 'contributor', 'modified',
                  'state', 'title', 'description', 'slug',
                  'thumbnail', 'description',
                  'url', 'license', 'activity', 'length', 'slides',
        )

class CourseSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False)
    contributor = UserSerializer(many=False)
    class Meta:
        model = Course
        fields = ('id',
                  'creator', 'created', 'contributor', 'modified',
                  'state', 'title', 'description', 'slug',
                  'thumbnail', 'description')