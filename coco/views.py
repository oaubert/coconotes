from collections import namedtuple, OrderedDict, Counter
import datetime
import itertools
import json

from actstream import action
from actstream.models import actor_stream, Action

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.sites.models import Site
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, render
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags, escape
from django.views.generic import CreateView, UpdateView, DeleteView, RedirectView, DetailView, ListView, View
from django.template.defaultfilters import pluralize
from django.contrib.staticfiles.templatetags.staticfiles import static

from rest_framework import permissions, viewsets
from extra_views import UpdateWithInlinesView, InlineFormSet

from .models import Channel, Video, Newsitem, Chapter, Activity, Annotation, Comment, AnnotationType, Resource, UserMetadata
from .models import VISIBILITY_PUBLIC, VISIBILITY_PRIVATE, TYPE_QUIZ, TYPE_NOTES
from .serializers import ChannelSerializer, ChapterSerializer, ActivitySerializer, VideoSerializer
from .serializers import AnnotationSerializer, CommentSerializer, ResourceSerializer, NewsitemSerializer, AnnotationTypeSerializer
from .utils import generic_search, update_object_history, log_access
from .permissions import IsOwnerOrReadOnly
from .forms import AnnotationEditForm, CommentEditForm
from .templatetags.coco import parse_timecode
from .actions import registry

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

class CommentDetailView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['pk'])
        return comment.parent_annotation.contextualized_link

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

class GroupActivityView(DetailView):
    model = Group
    template_name = 'group_activity.html'

    def get_queryset(self):
        return self.request.user.groups.all()

    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.GET.get('format') == 'json':
            return self.render_to_json_response(context)
        else:
            return super(GroupActivityView, self).render_to_response(context)

    def render_to_json_response(self, context):
        """Generate JSON data for group activity
        """
        group = self.get_object()
        # Build pseudo-activity from annotations for now.
        data = {
            'actions': [ {
                "actor": {
                    "username": a.contributor.username,
                    "fullname": a.contributor.get_full_name()
                } if a.is_updated else {
                    "username": a.creator.username,
                    "fullname": a.creator.get_full_name()
                },
                "verb": "updated" if a.is_updated else "created",
                "object": {
                    "uuid": a.uuid,
                    "url": a.contextualized_link,
                    "type": "annotation",
                    "title": a.title_or_description
                },
                "date": a.modified,
                "date_natural": naturaltime(a.modified),
                "video": {
                    "uuid": a.video.uuid,
                    "url": a.video.get_absolute_url(),
                    "title": a.video.title,
                    "thumbnail": a.video.thumbnail_url(),
                }
            } for a in group.metadata.annotations ]
        }
        return JsonResponse(data)

class VideoDetailView(DetailView):
    model = Video
    context_object_name='video'

    def get_context_data(self, **kwargs):
        context = super(VideoDetailView, self).get_context_data(**kwargs)
        try:
            context['groups'] = [ t[0]
                                  for t in self.request.user.metadata.tabconfig()
                                  if t[1] ]
        except AttributeError:
            # AnonymousUser does not have a metadata field
            context['groups'] = [ ]
        if self.request.user.is_authenticated():
            action.send(self.request.user, verb='accessed', action_object=self.object, url=self.request.path)
        return context

@log_access
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

@login_required
@log_access
def profile(request, **kw):
    return render_to_response('profile.html', {
        'username': request.user.username,
        'default_avatar': static('img/default_user.svg'),
        'annotationscount': Annotation.objects.filter(creator=request.user).count(),
        'current_document': 'profile',
    }, context_instance=RequestContext(request))

@login_required
@log_access
def userprofile(request, username=None):
    user = get_object_or_404(User, username=username)
    return render_to_response('userprofile.html', {
        'username': username,
        'other': user,
        'default_avatar': static('img/default_user.svg'),
        'current_document': 'profile',
    }, context_instance=RequestContext(request))

# Element: ["title", "description" ],
MODEL_MAP = OrderedDict((
    (Channel, ["title", "description", "category", "syllabus"]),
    (Video, ["title", "description"]),
    (Annotation, ["title", "description", "contentdata"]),
    (Comment, ["title", "description", "contentdata"]),
))

SNIPPET_MAX_LENGTH = 150
def get_snippet(query, element, fields=None):
    """Return the first matching snippet for an element.
    """
    if fields is None:
        fields = MODEL_MAP[type(element)]
    for field in fields:
        s = getattr(element, field)
        # Assume that query has been normalized to lowercase
        i = s.lower().find(query)
        if i > -1:
            snippet = s
            if len(snippet) <= SNIPPET_MAX_LENGTH:
                return snippet
            if i > SNIPPET_MAX_LENGTH / 2:
                snippet = u"\u2026" + snippet[i - SNIPPET_MAX_LENGTH / 2:]
            if len(snippet) > SNIPPET_MAX_LENGTH:
                snippet = snippet[:SNIPPET_MAX_LENGTH - 1] + u"\u2026"
            return snippet
    return ""

@log_access
def search(request, **kw):
    if request.user.is_authenticated():
        action.send(request.user, verb='searched', query=request.GET.get("q", "").strip())
    found = {}

    for model, fields in MODEL_MAP.iteritems():
        found[model] = [ el
                         for el in generic_search(request, model, fields, 'q')
                         if el.can_access(request.user) ]

    comments = {}
    # Add annotations from matching comments to matching annotations
    for comment in found[Comment]:
        if not comment.parent_annotation in found[Annotation]:
            found[Annotation].append(comment.parent_annotation)
            comments.setdefault(comment.parent_annotation, []).append(comment)

    # Filter out quiz elements
    found[Annotation] = [ el
                          for el in found[Annotation]
                          if el.annotationtype.title != TYPE_QUIZ ]
    found[Annotation].sort(key=lambda a: a.begin)

    # Videos corresponding to matching annotations
    containing_videos = set(a.video for a in found[Annotation])
    # Remove these videos from matching videos
    found[Video] = set(found[Video]) - containing_videos

    # Add channels
    containing_channels = set(v.channel for v in containing_videos)
    found[Channel] = set(found[Channel]) - containing_channels

    # Count number of annotations of different types
    counter = Counter(el.element_type for el in found[Annotation])
    counts = [(value, name) for (name, value) in counter.iteritems()]
    # Add count number for other elements
    counts = [ (len(found[model]), model.__name__) for model in (Comment, Channel, Video) ] + counts

    # Build element list (list of [ { element: el, children: [ {}...] } ])
    query = request.GET.get("q", "").strip().lower()

    # First annotations (and their containing_videos)
    annotated_videos = [ { 'element': v,
                           'snippet': get_snippet(query, v, [ "description" ]),
                           'children': [ { 'element': a,
                                           'creator': a.creator if a.annotationtype.title == TYPE_NOTES else "",
                                           'snippet': get_snippet(query, a) or a.title_or_description,
                                           'children': [ { 'element': c,
                                                           'creator': c.creator,
                                                           'snippet': get_snippet(query, c) or c.title_or_description }
                                                         for c in comments.get(a, []) ] }
                                         for a in found[Annotation]
                                         if a.video == v ]
                         }
                         for v in containing_videos ]
    # Next all other elements
    elements = [ { 'element': e,
                   'snippet': get_snippet(query, e) or e.title_or_description }
                 for e in itertools.chain(found[Channel], found[Video]) ]

    summary = u" ".join(
        u'<span data-type="%(name)s" class="result_type result_filter result_type-%(name)s">%(count)d %(name)s%(plural)s</span>' % {
            'name': name.rstrip('s'),
            'count': count,
            'plural': pluralize(count)
        } for (count, name) in counts if count)
    return render_to_response('search.html', {
        'summary': summary,
        'elements': elements,
        'annotated_videos': annotated_videos,
        'username': request.user.username,
        'query_string': request.GET.get('q', ''),
        'current_document': 'search',
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
    context = CocoContext(user=request.user,
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
    # We get data serialized by ldt_annotate
    # {"id":"f98d0acb-e7d8-f37a-6b67-6fb7a1282ebe","begin":0,"end":0,"content":{"data":{},"description":"Test","title":""},"tags":[],"media":"e7e856b1-dd32-44fa-8dda-56edab47729c","type_title":"Contributions","type":"ee3b536e-b8d7-428b-9df1-5283b72ef0ed","meta":{"created":"2015-11-25T16:00:02.141Z"}}
    data = json.loads(request.body.decode('utf-8'))
    # Validity checks...
    video = get_object_or_404(Video, uuid=data['media'])
    atype = get_object_or_404(AnnotationType, uuid=data['type'])
    # FIXME: check that type_title is consistent with type ?

    promoted = int(request.user in video.activity.chapter.teachers.all())

    # Create the annotation
    an = Annotation(uuid=data['id'],
                    creator=request.user,
                    contributor=request.user,
                    modified=datetime.datetime.now(),
                    annotationtype=atype,
                    video=video,
                    promoted=promoted,
                    begin=long(data['begin']) / 1000.0,
                    end=long(data['end']) / 1000.0,
                    title=data['content']['title'],
                    description=data['content']['description'])
    an.visibility_deserialize(data['sharing'])
    an.save()
    update_object_history(request, an, action='addition')
    context = CocoContext(user=request.user,
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
            'sharing': an.visibility_serialize
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
        an.visibility_deserialize(data['sharing'])
        an.save()
        update_object_history(request, an)
        # FIXME: check how to populate django changelist
        context = CocoContext(user=request.user,
                              video=an.video,
                              teacher_set=[t.pk for t in an.video.activity.chapter.teachers.all()],
                              current_group='')
        return JsonResponse({'annotations': [an.cinelab(context=context)]})
    elif request.method == 'DELETE':
        # Update the contributor property, which will be used to trace deletion activity actor
        an.contributor = request.user
        an.delete()
        update_object_history(request, an, action='deletion')
        return JsonResponse({'id': pk})

@login_required
@require_http_methods(["POST"])
def annotation_comment(request, pk=None, **kw):
    an = get_object_or_404(Annotation, pk=pk)
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        # Attributes: body, creator
        # FIXME: use https://bleach.readthedocs.org/en/latest/index.html to sanitize input
        desc = escape(strip_tags(data['description']))
        c = Comment(parent_annotation=an,
                    creator=request.user,
                    contributor=request.user,
                    description=desc,
                    group=an.group,
                    visibility=an.visibility)
        c.save()
        update_object_history(request, c)
        return JsonResponse({'comment': c.serialize()})

@login_required
@require_http_methods(["GET", "POST", "DELETE"])
def comment_edit(request, pk=None, **kw):
    comment = get_object_or_404(Comment, pk=pk)
    u = request.user
    if comment.creator != u and comment.contributor != u:
        return HttpResponse(status=403)
    if request.method == 'GET':
        f = CommentEditForm(initial={
            'title': comment.title,
            'description': comment.description,
            'sharing': comment.visibility_serialize,
            'annotation': comment.parent_annotation.uuid
            }, user=request.user, comment=comment)
        return render(request, 'coco/comment_form.html', {'form': f})
    elif request.method == 'POST':
        f = CommentEditForm(request.POST, user=request.user, comment=comment)
        if f.is_valid():
            comment.description = f.cleaned_data['description']
            comment.title = f.cleaned_data['title'] or ""
            comment.visibility_deserialize(f.cleaned_data['sharing'])
            comment.contributor = request.user
            comment.save()
            update_object_history(request, comment)
            return JsonResponse({'comment': comment.serialize()})
        else:
            return render(request, 'coco/comment_form.html', {'form': f})
    elif request.method == 'DELETE':
        # Update the contributor property, which will be used to trace deletion activity actor
        comment.contributor = request.user
        comment.delete()
        update_object_history(request, comment, action='deletion')
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
        update_object_history(request, an)
        context = CocoContext(user=request.user,
                              video=an.video,
                              teacher_set=[u.pk for u in an.video.activity.chapter.teachers.all()],
                              current_group='')
        return JsonResponse(an.cinelab(context=context))

@permission_required("annotation_change")
@require_http_methods(["GET", "POST"])
def toggle_annotation(request, pk=None, prop=None, **kw):
    """Toggle a property on an annotation.

    The property is either featured or public.
    """
    an = get_object_or_404(Annotation, pk=pk)
    if prop not in ('featured', 'public'):
        return HttpResponse("Invalid property", status=405)
    if request.method == 'GET':
        if prop == 'featured':
            value = an.promoted
        elif prop == 'public':
            value = (an.visibility == VISIBILITY_PUBLIC)
        return JsonResponse({prop: value})
    elif request.method == 'POST':
        if prop == 'featured':
            an.promoted = int(not an.promoted)
        elif prop == 'public':
            if an.visibility == VISIBILITY_PUBLIC:
                an.visibility = VISIBILITY_PRIVATE
            else:
                an.visibility = VISIBILITY_PUBLIC
        an.save()
        update_object_history(request, an)
        context = CocoContext(user=request.user,
                              video=an.video,
                              teacher_set=[u.pk for u in an.video.activity.chapter.teachers.all()],
                              current_group='')
        return JsonResponse(an.cinelab(context=context))

@login_required
@require_http_methods(["GET", "POST"])
def log_action(request, **kw):
    if request.method == 'GET':
        homepage = 'https://' + Site.objects.get_current().domain
        # Dump activity log as TinCanAPI json
        if request.GET.get('compact'):
            return JsonResponse({ 'stream': [
                {'actor': a.actor.username,
                 'verb': a.verb,
                 'object': { "id": a.action_object.get_absolute_url() if a.action_object else "",
                             "definition": {
                                 "name": a.action_object.title_or_description if a.action_object else "",
                             },
                             "extensions": a.data
                 },
                 'result': a.data.get('result', {}) if a.data else {},
                 'timestamp': a.timestamp.isoformat(),
                } for a in actor_stream(request.user)]
            })
        else:
            return JsonResponse({ 'stream': [
                {'actor': { "name": a.actor.get_full_name(),
                            "account": {
                                "homePage": homepage,
                                "name": a.actor.username,
                            }
                },
                 'verb': { "id": registry.get(a.verb, "http://comin-ocw.org/schema/1.0/%s" % a.verb),
                           "display": {
                               "en-US": a.verb
                           }
                 },
                 'object': { "id": a.action_object.get_absolute_url() if a.action_object else "",
                             "definition": {
                                 "name": a.action_object.title_or_description if a.action_object else "",
                             },
                             "extensions": a.data
                 },
                 'result': a.data.get('result', {}) if a.data else {},
                 'timestamp': a.timestamp.isoformat(),
                } for a in actor_stream(request.user)]
            })
    elif request.method == 'POST':
        # Get action info from POST data
        # { action: "action_name", object: "object_id" }
        # played -> video id
        try:
            info = json.loads(request.body.decode('utf-8'))
        except:
            return HttpResponse("Malformed data", status=400)
        verb = info.get('action', None)
        if verb == 'played' or verb == 'paused':
            vid = info.get('object', None)
            try:
                obj = Video.objects.get(pk=vid)
                action.send(request.user, verb=verb, action_object=obj)
            except Video.DoesNotExist:
                action.send(request.user, verb=verb, videoid=vid)
        elif verb is None:
            # Maybe it is analytics info from Quiz module:
            #            data = {
            #                "username": user,
            #                "useruuid": user_id,
            #                "subject": question,
            #                "property": prop,
            #                "value": val,
            #                "session": _this.session_id
            #            };
            # with property in wrong_answer right_answer skipped_answer useful useless skipped_vote
            prop = info.get('property', None)
            if prop:
                try:
                    question = Annotation.objects.get(pk=info.get('subject', ''))
                except:
                    question = None
                if prop == 'right_answer' or prop == 'wrong_answer':
                    action.send(request.user, verb='answered', action_object=question, result={"success": (prop == "right_answer"),
                                                                                               "value": info.get('value')})
                elif prop == 'skipped_answer':
                    action.send(request.user, verb='skipped', action_object=question)
                elif prop == 'useful' or prop == 'useless':
                    action.send(request.user, verb='rated', action_object=question, result={"score": 1 if prop == 'useful' else -1 })
        return HttpResponse(status=200)


class UserSetting(View):
    """Manipulate user settings.
    """
    WHITELIST = [
        'tabconfig' # Ordered list of (group_id, is_visible) tuples
    ]

    def get(self, request, name=None, **kw):
        if name not in self.WHITELIST:
            return HttpResponse(status=422)
        config = request.user.metadata.config or {}
        return JsonResponse({name: config.get(name, "")})

    def post(self, request, name=None, **kw):
        if name not in self.WHITELIST:
            return HttpResponse(status=422)
        data = json.loads(request.body.decode('utf-8'))
        if not isinstance(data, {}) or name not in data:
            # We are expecting a dict with the parameter name as key
            return HttpResponse(status=422)
        if request.user.metadata.config is None:
            request.user.metadata.config = {}
        request.user.metadata.config[name] = data.get(name)
        request.user.metadata.save()
        return JsonResponse({name: request.user.metadata.config.get(name, "")})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserSetting, self).dispatch(*args, **kwargs)

class UserSettingForm(UserSetting):
    """Display user settings form
    """
    def get(self, request, name=None, **kw):
        if name not in self.WHITELIST:
            return HttpResponse(status=422)
        return render_to_response('account/%s_form.html' % name,
                                  context_instance=RequestContext(request))

    def post(self, request, name=None, **kw):
        if name not in self.WHITELIST:
            return HttpResponse(status=422)
        if name == 'tabconfig':
            groups = [ (int(gid),
                        request.POST.get(gid) == 'on')
                       for gid in request.POST.getlist('reference') ]
            if request.user.metadata.config is None:
                request.user.metadata.config = {}
            request.user.metadata.config[name] = groups
            request.user.metadata.save()
            return HttpResponseRedirect(request.GET.get('next', ''))
        return HttpResponse(content="Invalid parameter", status=422)


class UserMetadataInline(InlineFormSet):
    model = UserMetadata
    fields = ['description', 'thumbnail' ]
    can_delete = False


class UpdateProfile(UpdateWithInlinesView):
    model = User
    inline_model = UserMetadata
    fields = ['first_name', 'last_name']
    inlines = [UserMetadataInline]

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('profile')

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["GET"])
def access_log(request, *args, **kw):
    # Cache of group information, indexed by username. Contains list of groupnames.
    GROUPCACHE = {}
    # Cache of video object indexed by content type id then uuid
    OBJECT_CACHE = {}

    def get_action_object(a):
        obj = None
        try:
            obj = OBJECT_CACHE[a.action_object_content_type_id][a.action_object_object_id]
        except KeyError:
            obj = a.action_object
        return obj

    def serialize_action(a):
        username = a.actor.username
        s = { 'timestamp': a.timestamp.isoformat(),
              'actor': username,
              'verb': a.verb }
        gs = GROUPCACHE.get(username)
        if gs is None:
            gs = a.actor.groups.values_list('name')
        if len(gs) == 1:
            g = gs[0]
        else:
            g = 'multiple'
        s['actor_group'] = g

        obj = get_action_object(a)
        if obj:
            s['object_type'] = unicode(obj.element_type)
            s['object_name'] = obj.title_or_description
            s['object_url'] = obj.get_absolute_url()
        else:
            s['object_type'] = ""
            s['object_name'] = ""
            s['object_url'] = ""
        if a.data:
            for k in ('url', 'query'):
                v = a.data.get(k, '')
                if v:
                    s[k] = v
            v = a.data.get('result')
            if v:
                try:
                    s['score'] = v.get('score', '')
                    s['success'] = v.get('success', '')
                except AttributeError:
                    # Maybe a unicode string
                    s['result'] = v
        s['target'] = a.target or ""
        return s

    def stream_serializer():
        """Generate a string stream of the JSON list serialization
        """
        yield '['
        # Note: we cannot use prefetch_related on action_object since it is not homogeneous.
        # Cf https://djangosnippets.org/snippets/2492/ if there is a need to further optimize.
        it = Action.objects.all().prefetch_related('actor')
        # We do not use .iterator() since it would disable the
        # prefetch_related effect.  And anyway, even using .iterator()
        # does not disable data caching so the whole data structure
        # will be loaded in memory.  What is gained from using a
        # StreamingHttpResponse is avoiding to store the whole json
        # representation.
        it = iter(it)
        yield json.dumps(serialize_action(it.next()), cls=DjangoJSONEncoder)
        for a in it:
            yield ",\n" + json.dumps(serialize_action(a), cls=DjangoJSONEncoder)
        yield ']\n'

    # Initialize GROUPCACHE
    for name, group in User.objects.values_list('username', 'groups__name'):
        GROUPCACHE.setdefault(name, []).append(group)

    # Initialize OBJECT_CACHE:
    for t in (Video, Annotation):
        ct = ContentType.objects.get_for_model(t).pk
        d = OBJECT_CACHE[ct] = {}
        if hasattr(t, 'annotationtype'):
            queryset = t.objects.prefetch_related('annotationtype').all()
        else:
            queryset = t.objects.all()

        for o in queryset:
            d[str(o.pk)] = o

    if settings.DEBUG and request.GET.get('debug'):
        # Enable debugging (esp. query count) through django-debug-toolbar
        return HttpResponse(content='<html><head><title>test</title></head><body><h1>OK</h1><pre>%s</pre></body></html>' % "".join(stream_serializer()), status=200)
    else:
        return HttpResponse("".join(stream_serializer()),
                            content_type='application/json')

@login_required
@require_http_methods(["GET"])
def stats(request, *args, **kw):
    """Generate global stats
    """
    data = {
        str(v.pk): v.summarized_information()
        for v in Video.objects.all()
    }
    return JsonResponse(data)
