from django.shortcuts import render_to_response
from django.template import RequestContext
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import Course, Video, Newsitem, Module
from .serializers import CourseSerializer, VideoSerializer

class CourseList(generics.ListCreateAPIView):
    model = Course
    serializer_class = CourseSerializer

class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Course
    serializer_class = CourseSerializer

class VideoList(generics.ListCreateAPIView):
    model = Video
    serializer_class = VideoSerializer

class VideoDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Video
    serializer_class = VideoSerializer

def home(request, **kw):
    return render_to_response('root.html', {
        'news': Newsitem.objects.order_by('-published')[:3],
        'une_items': Module.objects.order_by('-created')[:3],
        'last_videos': Video.objects.order_by('-created')[:4],
        'username': request.user.username,
    }, context_instance=RequestContext(request))
