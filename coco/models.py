from collections import Counter
from datetime import datetime
import itertools
import json
import uuid

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.defaultfilters import pluralize
from django.utils.translation import ugettext_lazy as _

from annoying.fields import AutoOneToOneField
from taggit_autosuggest.managers import TaggableManager
from taggit.models import TaggedItemBase
from sorl.thumbnail import ImageField

from fields import SlugOrNullField

from .templatetags.coco import format_timecode

TYPE_SLIDES = 'Slides'

# Monkeypatch support for serializing uuids to json. This allows it to
# be enabled for external libs such as ajaxselect
JSONEncoder_olddefault = json.JSONEncoder.default


def jsonencoder_newdefault(self, obj):
    if isinstance(obj, User):
        return obj.username
    elif isinstance(obj, Group):
        return obj.name
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return unicode(obj)
    else:
        return JSONEncoder_olddefault(self, obj)
json.JSONEncoder.default = jsonencoder_newdefault


class TaggedChannel(TaggedItemBase):
    content_object = models.ForeignKey('Channel')


class TaggedChapter(TaggedItemBase):
    content_object = models.ForeignKey('Chapter')


class TaggedActivity(TaggedItemBase):
    content_object = models.ForeignKey('Activity')


class TaggedVideo(TaggedItemBase):
    content_object = models.ForeignKey('Video')


class TaggedAnnotation(TaggedItemBase):
    content_object = models.ForeignKey('Annotation')


class TaggedComment(TaggedItemBase):
    content_object = models.ForeignKey('Comment')

JSON_MIMETYPES = [
    'application/json',
    'application/x-video-quiz'
    ]

# Visibility constants
VISIBILITY_PRIVATE = 1
VISIBILITY_GROUP = 2
VISIBILITY_PUBLIC = 3
VISIBILITY_CHOICES = ((VISIBILITY_PRIVATE, _("Private")),
                      (VISIBILITY_GROUP, _("Group")),
                      (VISIBILITY_PUBLIC, _("Public")))


class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return datetime.now()


class Element(models.Model):
    DEFAULT_AVATAR = static("img/default.png")
    class Meta:
        abstract = True
        ordering = ("-promoted", "-modified", "title")
        get_latest_by = "modify"

    uuid = models.UUIDField(primary_key=True,
                            default=uuid.uuid4,
                            editable=False)

    creator = models.ForeignKey(User, related_name='created_%(class)s', null=True)

    created = models.DateTimeField(_('Creation date'),
                                   help_text=_('Element creation date'),
                                   null=True, editable=True,
                                   default=datetime.now)

    contributor = models.ForeignKey(User, related_name='modified_%(class)s',
                                    blank=True, null=True)

    modified = AutoDateTimeField(_('Modification date'),
                                 help_text=_('Element modification date'),
                                 null=True, editable=True)

    state = models.CharField(_("State"),
                             max_length=16,
                             blank=True, default="draft")

    title = models.CharField(_("Title"),
                             blank=True,
                             max_length=250)

    description = models.TextField(_("Description"),
                                   blank=True)

    slug = SlugOrNullField(max_length=128,
                           null=True, unique=True, blank=True)

    thumbnail = ImageField(upload_to='thumbnails',
                           blank=True,
                           null=True)

    promoted = models.IntegerField(_("Promoted"),
                                   help_text=_('Promoted level - 0 by default'),
                                   default=0)

    @property
    def subtitle(self):
        """Subtitle for the element.
        """
        return ""

    @property
    def subtitle_link(self):
        """Subtitle link for the element.
        """
        return ""

    def thumbnail_url(self):
        """Return the thumbnail URL.
        """
        if self.thumbnail:
            return self.thumbnail.url
        else:
            return self.DEFAULT_AVATAR

    def get_absolute_url(self):
        return reverse('view-%s-detail' % self.__class__.__name__.lower(), args=[str(self.slug or self.pk)])

    def __unicode__(self):
        return u"%s (%s)" % (self.title_or_description,
                             self.__class__.__name__)
    @property
    def edit_url(self):
        return reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name), args=(self.pk,))

    @property
    def element_type(self):
        return _(self.__class__.__name__)

    @property
    def title_or_description(self):
        return self.title or self.description.splitlines()[0]

    def element_information(self):
        return self.element_type

    @property
    def is_updated(self):
        return abs((self.modified - self.created).total_seconds()) > 2

    def can_access(self, user):
        """Can the given user access this resource?
        """
        return True

class License(models.Model):
    slug = models.SlugField(max_length=16,
                            null=True, unique=True, blank=True)

    title = models.CharField(_("Title"),
                             blank=True,
                             max_length=250)

    url = models.URLField(_("URL"),
                          blank=True,
                          max_length=250)

    thumbnail = ImageField(upload_to='thumbnails')

    def __unicode__(self):
        return self.title


class Resource(Element):
    url = models.URLField(_("URL"),
                          blank=True,
                          max_length=250)

    license = models.ForeignKey(License,
                                blank=True,
                                null=True)

    # FIXME: to clarify
    # metadata = ???


class Channel(Element):
    DEFAULT_AVATAR = static("img/default_channel.svg")
    category = models.CharField(_("Category"),
                                blank=True,
                                max_length=20)

    syllabus = models.TextField(_("Syllabus"),
                                blank=True)

    tags = TaggableManager(blank=True, through=TaggedChannel)

    class Meta(Element.Meta):
        verbose_name = _('channel')
        verbose_name_plural = _('channels')

    @property
    def videos(self):
        """Videos associated with the channel.
        """
        return Video.objects.filter(activity__chapter__channel=self)

    @property
    def subtitle(self):
        return _("Channel")

    def element_information(self):
        n = len(self.videos)
        return _("Channel - %d video%s") % (n, pluralize(n))

class Chapter(Element):
    DEFAULT_AVATAR = static("img/default_chapter.svg")
    channel = models.ForeignKey(Channel)

    tags = TaggableManager(blank=True, through=TaggedChapter)

    teachers = models.ManyToManyField(User, related_name="teacher_for")

    class Meta(Element.Meta):
        verbose_name = _('chapter')
        verbose_name_plural = _('chapters')

    @property
    def subtitle(self):
        return _("Chapter")

    @property
    def videos(self):
        """Videos associated with the chapter.
        """
        return Video.objects.filter(activity__chapter=self)

    def element_information(self):
        n = len(self.videos)
        return _("Chapter - %d video%s") % (n, pluralize(n))

class Activity(Element):
    DEFAULT_AVATAR = static("img/default_video.svg")
    chapter = models.ForeignKey(Chapter)

    tags = TaggableManager(blank=True, through=TaggedActivity)

    class Meta(Element.Meta):
        verbose_name = _('activity')
        verbose_name_plural = _('activities')

    @property
    def subtitle(self):
        return self.chapter.title

    @property
    def subtitle_link(self):
        return self.chapter.get_absolute_url()


class Video(Resource):
    DEFAULT_AVATAR = static("img/default_video.svg")
    activity = models.ForeignKey(Activity,
                                 blank=True,
                                 null=True)
    duration = models.FloatField(_("Duration"),
                                 help_text=_("Video duration in seconds"),
                                 default=0)
    slides = models.ForeignKey(Resource,
                               blank=True,
                               null=True,
                               related_name="source_video")
    tags = TaggableManager(blank=True, through=TaggedVideo)

    class Meta(Element.Meta):
        verbose_name = _('video')
        verbose_name_plural = _('videos')

    @property
    def subtitle(self):
        return _("Video")

    @property
    def subtitle_link(self):
        return self.activity.get_absolute_url()

    def element_information(self):
        return format_timecode(self.duration)

    @property
    def has_slides(self):
        """Return True if the video has public Slides annotations.
        """
        return self.annotation_set.filter(visibility=VISIBILITY_PUBLIC, annotationtype__title=TYPE_SLIDES).count() > 0

    @property
    def channel(self):
        return self.activity.chapter.channel

    def latest_annotations(self, username, count=50):
        return self.annotation_set.filter(Q(creator__username=username) | Q(contributor__username=username)).order_by('-modified')[:count]

    def cinelab(self, context=None):
        """Return a cinelab serialization.
        """
        return {
            "id": self.uuid,
            "origin": "0",
            "unit": "ms",
            "http://advene.liris.cnrs.fr/ns/frame_of_reference/ms": "o=0",
            "url": self.url,
            "meta": {
                "coco:slug": self.slug or "",
                "coco:can_edit": (self.creator.username == context.username or self.contributor.username == context.username),
                "dc:contributor": self.contributor,
                "dc:creator": self.creator,
                "dc:created": self.created,
                "dc:modified": self.modified,
                "dc:title": self.title,
                "dc:description": self.description,
                "dc:duration": long(1000 * self.duration),
            }
        }


class UserContent(Element):
    contentdata = models.TextField(_("Content"),
                                   blank=True)
    contenttype = models.CharField(_("Content-Type"),
                                   max_length=127,
                                   default="text/plain",
                                   blank=True)
    visibility = models.SmallIntegerField(_("Visibility"),
                                          choices=VISIBILITY_CHOICES,
                                          help_text=_("Content visibility"),
                                          default=VISIBILITY_PRIVATE)

    def parsed_content(self, value=None):
        """Get or set value of contentdata.

        In case of json contenttype, encode data appropriately
        """
        if value is None:
            if self.contenttype in JSON_MIMETYPES:
                return json.loads(self.contentdata or '{}')
            else:
                return self.contentdata
        else:
            # Setting value
            if self.contenttype in JSON_MIMETYPES:
                value = json.dumps(value)
            self.contentdata = value

    def can_access(self, user):
        """Can the given user access this resource?
        """
        return (self.creator == user
                or self.contributor == user
                or user.is_staff
                or self.visibility == VISIBILITY_PUBLIC
                or (self.visibility == VISIBILITY_GROUP and user.groups.filter(name=self.group.name)))

    @property
    def subtitle(self):
        return _("User content")

    @property
    def visibility_as_string(self):
        if self.visibility == VISIBILITY_GROUP and self.group:
            return 'shared-%s' % self.group.id
        elif self.visibility == VISIBILITY_PUBLIC:
            return 'public'
        else:
            return 'private'


class AnnotationType(Element):
    """Annotation Type element

    It does not need more info than the one provided in Element.
    """
    class Meta(Element.Meta):
        verbose_name = _('annotation type')
        verbose_name_plural = _('annotation types')
        permissions = (
            ("slide_update", _("Can update slide content")),
            ("slide_delete", _("Can delete slide content")),
            ("slide_add", _("Can add slide content")),
        )

    def cinelab(self, context=None):
        """Return a cinelab serialization.
        """
        return {
            "id": self.uuid,
            "dc:contributor": self.contributor,
            "dc:creator": self.creator,
            "dc:created": self.created,
            "dc:modified": self.modified,
            "coco:can_edit": self.creator.username == context.username,
            "dc:title": self.title,
            "dc:description": self.description,
        }


class Annotation(UserContent):
    begin = models.FloatField(_("Begin"),
                              help_text=_("Annotation begin time (in seconds)"),
                              default=0)
    end = models.FloatField(_("End"),
                            help_text=_("Annotation end time (in seconds)"),
                            default=0)
    video = models.ForeignKey(Video)
    annotationtype = models.ForeignKey(AnnotationType,
                                       null=True)
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True)
    tags = TaggableManager(blank=True, through=TaggedAnnotation)

    class Meta(Element.Meta):
        verbose_name = _('annotation')
        verbose_name_plural = _('annotations')

    @property
    def element_type(self):
        return _(self.annotationtype.title)

    @property
    def subtitle(self):
        return ""

    @property
    def is_slide(self):
        return self.annotationtype.title == TYPE_SLIDES

    @property
    def contextualized_link(self):
        """Return the link to the contextualized annotation.
        """
        return "%s#t=%d&id=%s" % (reverse('view-video-detail', args=[str(self.video.pk)]),
                                  self.begin,
                                  self.uuid)

    def coco_category(self, context=None):
        cat = 'other'
        if context is None:
            return cat
        if self.creator.username == context.username:
            cat = 'own'
        elif self.creator.username in context.teacher_set:
            cat = 'teacher'
        return cat

    def cinelab(self, context=None):
        """Return a cinelab JSON serialization.
        """
        thumb = self.thumbnail.url if self.thumbnail.name else ''
        data = self.contentdata
        if self.contenttype in JSON_MIMETYPES:
            try:
                data = json.loads(self.contentdata)
            except ValueError:
                pass
        return {
            "id": self.uuid,
            "media": self.video.uuid,
            "type": self.annotationtype.uuid,
            "begin": long(self.begin * 1000),
            "end": long(self.end * 1000),
            "meta": {
                "coco:slug": self.slug or "",
                "coco:group": self.group.id if self.group else 0,
                "coco:category": self.coco_category(context),
                "coco:featured": self.promoted,
                "coco:can_edit": self.creator.username == context.username,
                "id-ref": self.annotationtype.uuid,
                "dc:contributor": self.contributor,
                "dc:creator": self.creator,
                "dc:created": self.created,
                "dc:modified": self.modified,
                "dc:title": self.title,
                "dc:description": self.description,
            },
            "content": {
                "mimetype": self.contenttype,
                # FIXME: investigate in MDP content.title vs meta.dc:title
                "title": self.title,
                "description": self.description,
                "data": data,
                "img": {
                    "src": thumb
                },
            },
            "tags": list(self.tags.values('name'))
        }


class Comment(UserContent):
    class Meta(Element.Meta):
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    parent_annotation = models.ForeignKey(Annotation,
                                          blank=True,
                                          null=True)
    parent_video = models.ForeignKey(Video,
                                     blank=True,
                                     null=True)
    parent_comment = models.ForeignKey('self',
                                       blank=True,
                                       null=True)
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True)
    tags = TaggableManager(blank=True, through=TaggedComment)


class Newsitem(Element):
    class Meta(Element.Meta):
        verbose_name = _('news item')
        verbose_name_plural = _('news items')

    category = models.CharField(_("Category"),
                                max_length=64,
                                blank=True,
                                default="")

    published = models.DateTimeField(_('Publication date'),
                                     help_text=_('Publication date'),
                                     null=True, editable=True)

    def get_absolute_url(self):
        return "%s#%s" % (reverse('view-newsitem-list'), self.pk)

    @property
    def subtitle(self):
        return self.category


class GroupMetadata(Element):
    DEFAULT_AVATAR = static("img/default_group.svg")
    class Meta(Element.Meta):
        verbose_name = _('group metadata')
        verbose_name_plural = _('group metadata')

    group = AutoOneToOneField(Group, related_name='metadata', unique=True)

    @property
    def annotations(self):
        return Annotation.objects.filter(group=self.group).filter(Q(visibility=VISIBILITY_PUBLIC) | Q(visibility=VISIBILITY_GROUP)).order_by("-modified")

    def __unicode__(self):
        return "Metadata for %s" % self.group.name

class UserMetadata(models.Model):
    DEFAULT_AVATAR = static("img/default_user.svg")
    class Meta:
        verbose_name = _('user metadata')
        verbose_name_plural = _('user metadata')

    user = AutoOneToOneField(User, related_name='metadata', unique=True)

    description = models.TextField(_("Description"),
                                   blank=True)

    thumbnail = ImageField(upload_to='thumbnails',
                           blank=True,
                           null=True)

    def __unicode__(self):
        return "Metadata for %s" % self.title

    @property
    def title(self):
        return self.user.username

    @property
    def thumbnail_url(self):
        """Return the thumbnail URL.
        """
        if self.thumbnail:
            return self.thumbnail.url
        else:
            return self.DEFAULT_AVATAR

    @property
    def annotations(self):
        return Annotation.objects.filter(Q(creator=self.user) | Q(contributor=self.user))

    def latest_annotations(self, count=50):
        """Return the latest n annotations.
        """
        return self.annotations.order_by('-modified')[:count]

    def summarized_information(self):
        """Return summarized information about annotations (grouped by Channel/Video)
        """
        def summarize_video(video, videoannotations):
            annotations = list(videoannotations)
            counter = Counter(a.visibility for a in annotations)
            return {
                'video': video,
                'total_annotations': len(annotations),
                'private_annotations': counter[VISIBILITY_PRIVATE],
                'public_annotations': counter[VISIBILITY_PUBLIC],
                'group_annotations': counter[VISIBILITY_GROUP]
            }
        return [
            {
                'channel': channel,
                'videos': [
                    summarize_video(video, videoannotations)
                    for video, videoannotations in itertools.groupby(annotations,
                                                                     lambda a: a.video)
                ]
            }
            for channel, annotations in itertools.groupby(self.annotations.select_related().order_by('video__activity__chapter__channel', 'video'),
                                                          lambda a: a.video.activity.chapter.channel)
        ]
