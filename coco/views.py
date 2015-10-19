import datetime
import json
from collections import namedtuple, OrderedDict

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, RedirectView

from rest_framework import permissions, viewsets

from .models import Course, Video, Newsitem, Module, Activity, Annotation, Comment, AnnotationType, Resource
from .serializers import CourseSerializer, ModuleSerializer, ActivitySerializer, VideoSerializer, AnnotationSerializer, CommentSerializer, ResourceSerializer, NewsitemSerializer, AnnotationTypeSerializer
from .utils import generic_search, COCoEncoder
from .permissions import IsOwnerOrReadOnly

class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Course.objects.all()
    lookup_field = 'uuid'
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,
                        contributor=self.request.user)

class ModuleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Module.objects.all()
    lookup_field = 'uuid'
    serializer_class = ModuleSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,
                        contributor=self.request.user)

class ActivityViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Activity.objects.all()
    lookup_field = 'uuid'
    serializer_class = ActivitySerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,
                        contributor=self.request.user)

class VideoViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Video.objects.all()
    lookup_field = 'uuid'
    serializer_class = VideoSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,
                        contributor=self.request.user)

class AnnotationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Annotation.objects.all()
    lookup_field = 'uuid'
    serializer_class = AnnotationSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,
                        contributor=self.request.user)

class AnnotationTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = AnnotationType.objects.all()
    lookup_field = 'uuid'
    serializer_class = AnnotationTypeSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,
                        contributor=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Comment.objects.all()
    lookup_field = 'uuid'
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,
                        contributor=self.request.user)

class ResourceViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Resource.objects.all()
    lookup_field = 'uuid'
    serializer_class = ResourceSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,
                        contributor=self.request.user)

class NewsitemViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Newsitem.objects.all()
    lookup_field = 'uuid'
    serializer_class = NewsitemSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,
                        contributor=self.request.user)

class AnnotationDetailView(RedirectView):
    permanent = False
    def get_redirect_url(self, *args, **kwargs):
        annotation = get_object_or_404(Annotation, pk=kwargs['pk'])
        return annotation.contextualized_link

class AnnotationCreateView(CreateView):
    model = Annotation
    fields = ('begin', 'end', 'group',
              'title', 'shorttitle',
              'description', 'slug', 'thumbnail',
              'annotationtype', 'video',
              'contenttype', 'contentdata',
              'visibility')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.contributor = self.request.user
        form.instance.modified = datetime.datetime.now()
        return super(AnnotationCreateView, self).form_valid(form)

class AnnotationUpdateView(UpdateView):
    model = Annotation
    fields = ('begin', 'end', 'group',
              'title', 'shorttitle',
              'description', 'slug', 'thumbnail',
              'annotationtype', 'video',
              'contenttype', 'contentdata',
              'visibility')

    def form_valid(self, form):
        form.instance.contributor = self.request.user
        form.instance.modified = datetime.datetime.now()
        return super(AnnotationCreateView, self).form_valid(form)

class AnnotationDeleteView(DeleteView):
    model = Annotation

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
        'annotationscount': Annotation.objects.filter(creator=request.user).count(),
        'annotations': Annotation.objects.filter(creator=request.user).order_by("-created")[:10],
        'current_document': 'profile',
    }, context_instance=RequestContext(request))

#Element: ["title", "shorttitle", "description" ],
MODEL_MAP = OrderedDict((
    (Course, ["title", "shorttitle", "description", "category", "syllabus" ]),
    (Video, ["title", "shorttitle", "description" ]),
    (Module, [ "title", "shorttitle", "description" ]),
    (Activity, ["title", "shorttitle", "description" ]),
    (Annotation, ["title", "shorttitle", "description", "contentdata" ]),
    (Comment, ["title", "shorttitle", "description", "contentdata" ]),
    (Newsitem, ["title", "shorttitle", "description", "category" ]),
))
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

CocoContext = namedtuple('Context', [ 'username', 'teacher_set', 'current_group' ])

def cinelab(request, slug=None, pk=None, **kw):
    """Generate a cinelab package in json format for the given video.
    """
    if pk is not None:
        v = get_object_or_404(Video, pk=pk)
    elif slug is not None:
        v = get_object_or_404(Video, slug=slug)
    else:
        return HttpResponse(status=422)

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
    context = CocoContext(username=request.user.username,
                          teacher_set=[],
                          current_group='') # FIXME: get from cookie/session info?
    data['medias'].append(v.cinelab(context=context))
    data['annotations'].extend(a.cinelab(context=context) for a in Annotation.objects.filter(video=v))
    # Add defined annotation types + a selection of basic types
    data['annotation-types'].extend(a.cinelab(context=context) for a in AnnotationType.objects.all())
    return HttpResponse(json.dumps(data, cls=COCoEncoder, indent=1),
                        content_type="application/json")
