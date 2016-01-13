from collections import namedtuple, OrderedDict, Counter
import datetime
import json
import re

from django.conf import settings
from django.contrib.auth.models import Group
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, render
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, UpdateView, DeleteView, RedirectView, DetailView, ListView
from django.template.defaultfilters import pluralize
from django.contrib.staticfiles.templatetags.staticfiles import static
from rest_framework import permissions, viewsets


from .models import Channel, Video, Newsitem, Chapter, Activity, Annotation, Comment, AnnotationType, Resource
from .models import VISIBILITY_PRIVATE, VISIBILITY_GROUP, VISIBILITY_PUBLIC
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

class GroupListView(ListView):
    model = Group
    template_name = 'group_list.html'

    def get_queryset(self):
        return self.request.user.groups.all()

class GroupDetailView(DetailView):
    model = Group
    template_name = 'group_detail.html'

    def get_queryset(self):
        return self.request.user.groups.all()

class VideoDetailView(DetailView):
    model = Video
    context_object_name='video'

    def get_context_data(self, **kwargs):
        context = super(VideoDetailView, self).get_context_data(**kwargs)
        context['groups'] = self.request.user.groups.all()
        return context

def home(request, **kw):
    une_items = (list(Channel.objects.order_by('-promoted', '-modified')[:3])
                 + list(Video.objects.order_by('-promoted', '-modified')[:3]))
    une_items.sort(key=lambda o: -o.promoted)
    return render_to_response('home.html', {
        'news': Newsitem.objects.order_by('-published')[:3],
        'une_items': une_items[:3],
        'last_videos': Video.objects.order_by('-modified')[:4],
        'username': request.user.username,
        'current_document': 'home',
    }, context_instance=RequestContext(request))

def profile(request, **kw):
    return render_to_response('profile.html', {
        'username': request.user.username,
        'default_avatar': static('img/default_user.svg'),
        'annotationscount': Annotation.objects.filter(creator=request.user).count(),
        'current_document': 'profile',
    }, context_instance=RequestContext(request))

# Element: ["title", "description" ],
MODEL_MAP = OrderedDict((
    (Channel, ["title", "description", "category", "syllabus"]),
    (Video, ["title", "description"]),
    (Chapter, ["title", "description"]),
    (Annotation, ["title", "description", "contentdata"]),
    (Comment, ["title", "description", "contentdata"]),
))


def search(request, **kw):
    elements = []

    for model, fields in MODEL_MAP.iteritems():
        elements += [ el
                      for el in generic_search(request, model, fields, 'q')
                      if el.can_access(request.user) ]

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

CocoContext = namedtuple('Context', ['user', 'teacher_set', 'current_group', 'video'])

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
    context = CocoContext(user=request.user.pk,
                          teacher_set=[u.pk for u in v.activity.chapter.teachers.all()],
                          video=v,
                          current_group='')  # FIXME: get from cookie/session info?
    data['medias'].append(v.cinelab(context=context))
    data['annotations'].extend(a.cinelab(context=context)
                               for a in Annotation.objects.filter(video=v).prefetch_related('group', 'creator', 'contributor', 'annotationtype')
                               if a.can_access(request.user))
    # Add defined annotation types + a selection of basic types
    data['annotation-types'].extend(a.cinelab(context=context) for a in AnnotationType.objects.prefetch_related('creator', 'contributor').all())
    if settings.DEBUG and request.GET.get('debug'):
        return HttpResponse(content='<html><head><title>test</title></head><body><h1>OK</h1><pre>%s</pre></body></html>' % json.dumps(data, indent=2), status=200)
    else:
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
    context = CocoContext(user=request.user.pk,
                          video=video,
                          teacher_set=[u.pk for u in video.activity.chapter.teachers.all()],
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
            'title': an.title,
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
        an.title = data['title'] or ""
        an.begin = data['begin']
        if an.end < an.begin:
            an.end = an.begin
        m = re.search('^shared-(\d+)$', data['sharing'])
        if m:
            an.visibility = VISIBILITY_GROUP
            an.group = Group.objects.get(pk=long(m.group(1)))
        elif data['sharing'] == 'public':
            an.visibility = VISIBILITY_PUBLIC
        else:
            an.visibility = VISIBILITY_PRIVATE
        an.save()
        # FIXME: check how to populate django changelist
        context = CocoContext(user=request.user.pk,
                              video=an.video,
                              teacher_set=[t.pk for t in an.video.activity.chapter.teachers.all()],
                              current_group='')
        return JsonResponse(an.cinelab(context=context))
    elif request.method == 'DELETE':
        an.delete()
        return JsonResponse({'id': pk})


@permission_required("slide_update")
@require_http_methods(["GET", "POST", "DELETE"])
def slide_level(request, pk=None, **kw):
    an = get_object_or_404(Annotation, pk=pk)
    if not an.is_slide:
        return HttpResponse("Invalid slide annotation", status=405)
    if request.method == 'GET':
        data = an.parsed_content() or {}
        return JsonResponse({'level': data.get('level', 1)})
    elif request.method == 'POST':
        try:
            level = json.loads(request.body.decode('utf-8'))['level']
        except:
            return HttpResponse("Malformed data", status=400)
        if not an.contentdata:
            data = {}
            an.contenttype = "application/json"
        else:
            data = an.parsed_content()
        data['level'] = level
        an.parsed_content(data)
        an.save()
        # FIXME: check how to populate django logentries
        context = CocoContext(user=request.user.pk,
                              video=an.video,
                              teacher_set=[u.pk for u in an.video.activity.chapter.teachers.all()],
                              current_group='')
        return JsonResponse(an.cinelab(context=context))
