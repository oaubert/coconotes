from rest_framework import serializers
from .models import Channel, Chapter, Activity, Video, Annotation, AnnotationType, Resource, Comment, Newsitem
from django.contrib.auth.models import User, Group

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ( 'name', 'id' )

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ( 'username', 'first_name', 'last_name' )

class AnnotationTypeSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False)
    contributor = UserSerializer(many=False)
    class Meta:
        model = AnnotationType
        fields = ('uuid',
                  'creator', 'created', 'contributor', 'modified',
                  'state', 'title', 'description', 'slug',
                  'thumbnail', 'description')

class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False)
    contributor = UserSerializer(many=False)
    class Meta:
        model = Resource
        fields = ('uuid',
                  'creator', 'created', 'contributor', 'modified',
                  'state', 'title', 'description', 'slug',
                  'thumbnail', 'description',
                  'url', 'license')

class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False)
    contributor = UserSerializer(many=False)
    class Meta:
        model = Channel
        fields = ('uuid',
                  'creator', 'created', 'contributor', 'modified',
                  'state', 'title', 'description', 'slug',
                  'thumbnail', 'description')

class ChapterSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False)
    contributor = UserSerializer(many=False)
    channel = ChannelSerializer(many=False)
    class Meta:
        model = Chapter
        fields = ('uuid',
                  'creator', 'created', 'contributor', 'modified',
                  'state', 'title', 'description', 'slug',
                  'thumbnail', 'description',
                  'channel')

class ActivitySerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False)
    contributor = UserSerializer(many=False)
    chapter = ChapterSerializer(many=False)
    class Meta:
        model = Activity
        fields = ('uuid',
                  'creator', 'created', 'contributor', 'modified',
                  'state', 'title', 'description', 'slug',
                  'thumbnail', 'description',
                  'chapter')

class VideoSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False)
    contributor = UserSerializer(many=False)
    activity = ActivitySerializer(many=False)
    slides = ResourceSerializer(many=False)
    class Meta:
        model = Video
        fields = ('uuid',
                  'creator', 'created', 'contributor', 'modified',
                  'state', 'title', 'description', 'slug',
                  'thumbnail', 'description',
                  'url', 'license', 'activity', 'duration', 'slides',
        )

class AnnotationSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False)
    contributor = UserSerializer(many=False)
    video = VideoSerializer(many=False)
    annotationtype = AnnotationTypeSerializer(many=False)
    group = GroupSerializer(many=False)
    class Meta:
        model = Annotation
        fields = ('uuid',
                  'creator', 'created', 'contributor', 'modified',
                  'state', 'title', 'description', 'slug',
                  'thumbnail', 'description',
                  'begin', 'end', 'video', 'annotationtype',
                  'visibility', 'contentdata', 'contenttype',
                  'group',
                  'comment_set')

class CommentSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False)
    contributor = UserSerializer(many=False)
    parent_annotation = AnnotationSerializer(many=False)
    parent_video = VideoSerializer(many=False)
    class Meta:
        model = Comment
        fields = ('uuid',
                  'creator', 'created', 'contributor', 'modified',
                  'state', 'title', 'description', 'slug',
                  'thumbnail', 'description',
                  'visibility', 'contentdata', 'contenttype',
                  'group',
                  'comment_set')

class NewsitemSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False)
    contributor = UserSerializer(many=False)
    class Meta:
        model = Newsitem
        fields = ('uuid',
                  'creator', 'created', 'contributor', 'modified',
                  'state', 'title', 'description', 'slug',
                  'thumbnail', 'description',
                  'category', 'published')
