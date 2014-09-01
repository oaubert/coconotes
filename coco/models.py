from django.db import models
from django.contrib.auth.models import User
from taggit_autosuggest.managers import TaggableManager
from sorl.thumbnail import ImageField

from gettext import gettext as _

class Element(models.Model):
    class Meta:
        abstract = True

    creator = models.ForeignKey(User, related_name='%(class)s_created_by')

    created = models.DateTimeField(_('Creation date'),
                                   help_text=_('Element creation date'),
                                   null=True, editable=True,
                                   auto_now_add=True)

    contributor = models.ForeignKey(User, related_name='%(class)s_modified_by')

    modified = models.DateTimeField(_('Modification date'),
                                    help_text=_('Element modification date'),
                                    null=True, editable=True,
                                    auto_now_add=True)

    state = models.CharField(_("State"),
                             max_length=16,
                             blank=True, default="draft")

    title = models.CharField(_("Title"),
                             blank=True,
                             max_length=250)

    description = models.TextField(_("Description"),
                                   blank=True)

    slug = models.SlugField(max_length=128)

    thumbnail = ImageField(upload_to='thumbnails')

    tags = TaggableManager(blank=True)

class License(models.Model):
    title = models.CharField(_("Title"),
                             blank=True,
                             max_length=250)

    url = models.URLField(_("URL"),
                             blank=True,
                             max_length=250)

class Resource(Element):
    url = models.URLField(_("URL"),
                             blank=True,
                             max_length=250)

    license = models.ForeignKey(License,
                                null=True)

    # FIXME: to clarify
    # metadata = ???

class Course(Element):
    syllabus = models.TextField(_("Syllabus"),
                                blank=True)

class Module(Element):
    pass

class Activity(Element):
    pass

class Video(Resource):
    length = models.FloatField(_("Length"),
                                 help_text=_("Video length in seconds"),
                                 default=0)
    slides = models.ForeignKey(Resource,
                               null=True,
                               related_name="source_video")

class UserContent(Element):
    syllabus = models.TextField(_("Content"),
                                blank=True)
    visibility = models.CharField(_("Visibility"),
                                  max_length=16,
                                  help_text=_("Visibility (private, group, public)"),
                                  default="private")

class Annotation(UserContent):
    begin = models.FloatField(_("Begin"),
                              help_text=_("Annotation begin time (in seconds)"),
                              default=0)
    end = models.FloatField(_("End"),
                              help_text=_("Annotation end time (in seconds)"),
                              default=0)
    resource = models.ForeignKey(Resource)
    category = models.CharField(_("Category"),
                                max_length=64,
                                help_text=_("Category (question, suggestion...)"),
                                blank=True,
                                default="")


class Comment(UserContent):
    parent_annotation = models.ForeignKey(Annotation,
                                          null=True)
    parent_video = models.ForeignKey(Video,
                                     null=True)
    parent_comment = models.ForeignKey('self',
                                       null=True)
