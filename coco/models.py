from datetime import datetime
import json
import uuid

from django.db import models
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.translation import ugettext_lazy as _

from annoying.fields import AutoOneToOneField
from taggit_autosuggest.managers import TaggableManager
from taggit.models import TaggedItemBase
from sorl.thumbnail import ImageField

from fields import SlugOrNullField

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
    class Meta:
        abstract = True
        ordering = ("-promoted", "-modified", "title")

    uuid = models.UUIDField(primary_key=True,
                            default=uuid.uuid4,
                            editable=False)

    creator = models.ForeignKey(User, related_name='created_%(class)s')

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
            return static("img/default.png")

    def get_absolute_url(self):
        return reverse('view-%s-detail' % self.__class__.__name__.lower(), args=[str(self.slug or self.pk)])

    def __unicode__(self):
        return u"%s (%s)" % (self.title,
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
        return self.category

    def element_description(self):
        return _("Channel of %d videos") % len(self.videos)


class Chapter(Element):
    channel = models.ForeignKey(Channel)

    tags = TaggableManager(blank=True, through=TaggedChapter)

    teachers = models.ManyToManyField(User, related_name="teacher_for")

    class Meta(Element.Meta):
        verbose_name = _('chapter')
        verbose_name_plural = _('chapters')

    @property
    def subtitle(self):
        return self.channel.title

    @property
    def subtitle_link(self):
        return self.channel.get_absolute_url()


class Activity(Element):
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
        return self.activity.title

    @property
    def subtitle_link(self):
        return self.activity.get_absolute_url()

    @property
    def has_slides(self):
        """Return True if the video has public Slides annotations.
        """
        return self.annotation_set.filter(visibility=VISIBILITY_PUBLIC, annotationtype__title=TYPE_SLIDES).count() > 0

    @property
    def channel(self):
        return self.activity.chapter.channel

    def latest_annotations(self, count=10):
        return self.annotation_set.order_by('-modified')[:count]

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
                "coco:group": self.group.id if self.group else "",
                "coco:category": self.coco_category(context),
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

    @property
    def subtitle(self):
        return self.category


class GroupMetadata(Element):
    class Meta(Element.Meta):
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    group = AutoOneToOneField(Group)


class UserMetadata(models.Model):
    user = AutoOneToOneField(User)

    title = models.CharField(_("Title"),
                             blank=True,
                             max_length=250)

    description = models.TextField(_("Description"),
                                   blank=True)

    thumbnail = ImageField(upload_to='thumbnails',
                           blank=True,
                           null=True)
