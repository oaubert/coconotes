from django.shortcuts import render_to_response
from django.template import RequestContext
from rest_framework import generics
from .models import Course, Video, Newsitem, Module, Activity, Annotation, Comment
from .serializers import CourseSerializer, VideoSerializer
from .utils import generic_search

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
    return render_to_response('home.html', {
        'news': Newsitem.objects.order_by('-published')[:3],
        'une_items': Module.objects.order_by('-created')[:3],
        'last_videos': Video.objects.order_by('-created')[:4],
        'username': request.user.username,
        'current_document': 'home',
    }, context_instance=RequestContext(request))

def profile(request, **kw):
    return render_to_response('profile.html', {
        'username': request.user.username,
        'current_document': 'profile',
    }, context_instance=RequestContext(request))

MODEL_MAP = {
    #Element: ["title", "shorttitle", "description" ],
    Course: ["title", "shorttitle", "description", "category", "syllabus" ],
    Module: [ "title", "shorttitle", "description" ],
    Activity: ["title", "shorttitle", "description" ],
    Video: ["title", "shorttitle", "description" ],
    Annotation: ["title", "shorttitle", "description", "syllabus" ],
    Comment: ["title", "shorttitle", "description", "syllabus" ],
    Newsitem: ["title", "shorttitle", "description", "category" ],
}
def search(request, **kw):
    elements = []
    for model,fields in MODEL_MAP.iteritems():
        elements += generic_search(request, model, fields, 'q')

    return render_to_response('search.html', {
        'elements': elements,
        'username': request.user.username,
        'query_string' : request.GET.get('q', ''),
        'current_document': 'profile',
    }, context_instance=RequestContext(request))
