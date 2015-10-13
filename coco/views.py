import datetime
import json

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from rest_framework import generics

from .models import Course, Video, Newsitem, Module, Activity, Annotation, Comment, AnnotationType, Resource
from .serializers import CourseSerializer, VideoSerializer
from .utils import generic_search, COCoEncoder

class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    lookup_field = 'uuid'
    serializer_class = CourseSerializer

class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Course
    lookup_field = 'uuid'
    serializer_class = CourseSerializer

class VideoList(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    lookup_field = 'uuid'
    serializer_class = VideoSerializer

class VideoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    lookup_field = 'uuid'
    serializer_class = VideoSerializer

class ResourceList(generics.ListCreateAPIView):
    queryset = Resource.objects.all()
    lookup_field = 'uuid'

class ResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Resource
    lookup_field = 'uuid'

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
    Annotation: ["title", "shorttitle", "description", "contentdata" ],
    Comment: ["title", "shorttitle", "description", "contentdata" ],
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

def cinelab(request, video=None, **kw):
    """Generate a cinelab package in json format for the given video.
    """
    v = get_object_or_404(Video, pk=video)
    data = {
        "tags": [],
        "views": [],
        "lists": [],
        "medias": [],
        "annotations": [],
        "annotation-types": []
    }
    data['meta'] = {
        "dc:contributor": request.user.username,
        "dc:creator": request.user.username,
        "dc:title": v.title,
        "id": u"package_" + unicode(v.uuid),
        "dc:modified": datetime.datetime.now(),
        "dc:created": v.created,
        "main_media": unicode(v.uuid),
        "dc:description": ""
    }
    data['medias'].append(v.cinelab())
    data['annotations'].extend(a.cinelab() for a in Annotation.objects.filter(video=v))
    # Add defined annotation types + a selection of basic types
    data['annotation-types'].extend(a.cinelab() for a in AnnotationType.objects.all())
    return HttpResponse(json.dumps(data, cls=COCoEncoder, indent=1),
                        content_type="application/json")

