import datetime
import json
from collections import namedtuple, OrderedDict, Counter

from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, UpdateView, DeleteView, RedirectView, DetailView
from django.template.defaultfilters import pluralize
from django.contrib.staticfiles.templatetags.staticfiles import static
from rest_framework import permissions, viewsets


from .models import Channel, Video, Newsitem, Chapter, Activity, Annotation, Comment, AnnotationType, Resource
from .serializers import ChannelSerializer, ChapterSerializer, ActivitySerializer, VideoSerializer
from .serializers import AnnotationSerializer, CommentSerializer, ResourceSerializer, NewsitemSerializer, AnnotationTypeSerializer
from .utils import generic_search
from .permissions import IsOwnerOrReadOnly
from .forms import AnnotationEditForm
from .templatetags.coco import parse_timecode

class ChannelViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Channel.objects.all()
    lookup_field = 'uuid'
    serializer_class = ChannelSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,
                        contributor=self.request.user)


class ChapterViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Chapter.objects.all()
    lookup_field = 'uuid'
    serializer_class = ChapterSerializer

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
              'title',
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
    """Annotation edit view.

    Layout: TC  / Description
            This note is not shared.
            This note is shared with everyone.
            This note is shared  with GroupeN...

    """
    model = Annotation

    def get_form_kwargs(self):
        kwargs = super(AnnotationUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.contributor = self.request.user
        form.instance.modified = datetime.datetime.now()
        return super(AnnotationUpdateView, self).form_valid(form)


class AnnotationDeleteView(DeleteView):
    model = Annotation


class VideoDetailView(DetailView):
    model = Video
    context_object_name='video'

    def get_context_data(self, **kwargs):
        context = super(VideoDetailView, self).get_context_data(**kwargs)
        context['groups'] = self.request.user.groups.all()
        return context

def home(request, **kw):
    return render_to_response('home.html', {
        'news': Newsitem.objects.order_by('-published')[:3],
        'une_items': Chapter.objects.order_by('-promoted', '-modified')[:3],
        'last_videos': Video.objects.order_by('-modified')[:4],
        'username': request.user.username,
        'current_document': 'home',
    }, context_instance=RequestContext(request))


def profile(request, **kw):
    videos = [
        {
            'object': v,
            'latest_annotations': v.latest_annotations(request.user)
        }
        for v in Video.objects.filter(annotation__creator=request.user).annotate(count=Count('annotation')).order_by("-count")
    ]
    return render_to_response('profile.html', {
        'username': request.user.username,
        'default_avatar': static('img/default_user.svg'),
        'videos': videos,
        'annotationscount': Annotation.objects.filter(creator=request.user).count(),
        'current_document': 'profile',
    }, context_instance=RequestContext(request))

# Element: ["title", "description" ],
MODEL_MAP = OrderedDict((
    (Channel, ["title", "description", "category", "syllabus"]),
    (Video, ["title", "description"]),
    (Chapter, ["title", "description"]),
    (Activity, ["title", "description"]),
    (Annotation, ["title", "description", "contentdata"]),
    (Comment, ["title", "description", "contentdata"]),
    (Newsitem, ["title", "description", "category"]),
))


def search(request, **kw):
    elements = []

    for model, fields in MODEL_MAP.iteritems():
        elements += generic_search(request, model, fields, 'q')

    counts = Counter(el.element_type for el in elements)
    # Reorder counter info to match MODEL_MAP key order
    counts = [(value, name) for (name, value) in counts.iteritems()]
    map_order = dict((key.__name__, count) for (count, key) in enumerate(MODEL_MAP))
    counts.sort(key=lambda t: map_order.get(t[1], -1))
    summary = u", ".join(u"%d %s%s" % (count, name.rstrip('s'), pluralize(count))
                         for (count, name) in counts)
    return render_to_response('search.html', {
        'summary': summary,
        'elements': elements,
        'username': request.user.username,
        'query_string': request.GET.get('q', ''),
        'current_document': 'profile',
    }, context_instance=RequestContext(request))

CocoContext = namedtuple('Context', ['username', 'teacher_set', 'current_group'])

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
                          teacher_set=[u.username for u in v.activity.chapter.teachers.all()],
                          current_group='')  # FIXME: get from cookie/session info?
    data['medias'].append(v.cinelab(context=context))
    data['annotations'].extend(a.cinelab(context=context)
                               for a in Annotation.objects.filter(video=v)
                               if a.can_access(request.user))
    # Add defined annotation types + a selection of basic types
    data['annotation-types'].extend(a.cinelab(context=context) for a in AnnotationType.objects.all())
    return JsonResponse(data)


@login_required
def annotation_add(request, **kw):
    # We get data serialized by ldt
    # {"id":"f98d0acb-e7d8-f37a-6b67-6fb7a1282ebe","begin":0,"end":0,"content":{"data":{},"description":"Test","title":""},"tags":[],"media":"e7e856b1-dd32-44fa-8dda-56edab47729c","type_title":"Contributions","type":"ee3b536e-b8d7-428b-9df1-5283b72ef0ed","meta":{"created":"2015-11-25T16:00:02.141Z"}}
    data = json.loads(request.body.decode('utf-8'))
    # Validity checks...
    video = get_object_or_404(Video, uuid=data['media'])
    atype = get_object_or_404(AnnotationType, uuid=data['type'])
    # FIXME: check that type_title is consistent with type ?

    # Create the annotation
    an = Annotation(uuid=data['id'],
                    creator=request.user,
                    contributor=request.user,
                    modified=datetime.datetime.now(),
                    annotationtype=atype,
                    video=video,
                    begin=long(data['begin']) / 1000.0,
                    end=long(data['end']) / 1000.0,
                    title=data['content']['title'],
                    description=data['content']['description'])
    an.save()
    context = CocoContext(username=request.user.username,
                          teacher_set=[u.username for u in video.activity.chapter.teachers.all()],
                          current_group='')  # FIXME: get from cookie/session info?
    return JsonResponse(an.cinelab(context=context))


@login_required
@require_http_methods(["GET", "POST", "DELETE"])
def annotation_edit(request, pk=None, **kw):
    an = get_object_or_404(Annotation, pk=pk)
    u = request.user
    if an.creator != u and an.contributor != u:
        return HttpResponse(status=403)
    if request.method == 'GET':
        f = AnnotationEditForm(initial={
            'begin': an.begin,
            'description': an.description,
            'sharing': an.visibility_as_string
            }, user=request.user, annotation=an)
        return render(request, 'coco/annotation_form.html', {'form': f})
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        data['begin'] = parse_timecode(data['begin'])
        # Validity checks
        if data['begin'] > an.video.duration:
            data['begin'] = an.video.duration
        if data['begin'] < 0:
            data['begin'] = 0
        an.description = data['description']
        an.begin = data['begin']
        if an.end < an.begin:
            an.end = an.begin
        an.save()
        # FIXME: check how to populate django changelist
        context = CocoContext(username=request.user.username,
                              teacher_set=[u.username for u in an.video.activity.chapter.teachers.all()],
                              current_group='')
        return JsonResponse(an.cinelab(context=context))
    elif request.method == 'DELETE':
        an.delete()
        return JsonResponse({'id': pk})
