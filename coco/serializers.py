from rest_framework import serializers
from .models import Course, Video

class VideoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Video
        fields = ('pk', 
                  'creator', 'created', 'contributor', 'modified', 
                  'state', 'title', 'description', 'slug',
                  'tags', 'thumbnail', 'description',
                  'url', 'license', 'activity', 'length', 'slides'
        )

class CourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = ('pk', 
                  'creator', 'created', 'contributor', 'modified', 
                  'state', 'title', 'description', 'slug', 
                  'tags', 'thumbnail', 'description')
