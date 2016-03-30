import datetime

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin, UserAdmin

import adminactions.actions as actions
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.helpers import make_ajax_form

from .models import Channel, Video, Chapter, License, AnnotationType, Annotation, Comment, Resource, Newsitem, Activity
from .models import UserMetadata, GroupMetadata
from .models import VISIBILITY_PUBLIC

# register all adminactions
actions.add_to_site(admin.site)
admin.site.register(License)
admin.site.register(Resource)

class CreatorMixin(object):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        obj.contributor = request.user
        obj.save()

# Common fieldsets for all Elements
ELEMENT_FIELDSETS = [
    (None,               {'fields': [('slug', 'state', 'promoted')]}),
    (_("Metadata"),      {'fields': [('creator', 'created', 'contributor', 'modified')], 'classes': ['collapse']}),
    (_("Content"),       {'fields': [('title', 'thumbnail'), 'description']}),
    (_("Tags"),         {'fields': ['tags']})
]
USERCONTENT_FIELDSETS = [
    (_("User content"), {'fields': [('visibility', 'contenttype'),
                                    'contentdata']}),
]


class ElementAdmin(AjaxSelectAdmin, CreatorMixin, admin.ModelAdmin):
    class Media:
        js = ['js/admin_filter_collapse.js']

    save_on_top = True
    list_display = ('title', 'slug', 'promoted')
    search_fields = ('title',)

    prepopulated_fields = {'slug': ('title',)}
    list_select_related = True

    def get_changeform_initial_data(self, request):
        return {
            'creator': request.user.pk,
            'contributor': request.user.pk,
            'modified': datetime.datetime.now
        }

    def object_link(self, item):
        ret = u'<a title="Edit item" target="_blank" href="{adminurl}">\u270f</a> <a title="View on site" target="_blank" href="{absurl}">\u25ce</a>'.format(adminurl=item.pk, absurl=item.get_absolute_url())
        try:
            ret = ret + u'<a title="View source url" target="_blank" href="{url}">\u21eb</a>'.format(url=item.url)
        except AttributeError:
            pass
        return ret
    object_link.short_description = 'View'
    object_link.allow_tags = True


@admin.register(Video)
class VideoAdmin(ElementAdmin):
    list_display = ('object_link', 'promoted', 'title', 'description', 'slug', 'creator', 'duration', 'created', 'thumbnail')
    list_editable = ('promoted', 'title', 'slug', 'description', 'creator', 'duration', 'thumbnail')
    list_display_links = None
    list_filter = (('creator', admin.RelatedOnlyFieldListFilter),
                   'promoted')
    search_fields = ('title', 'slug')

    form = make_ajax_form(Video, {'activity': 'activity',
                                  'creator': 'user',
                                  'contributor': 'user'})
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        (_("Video specific"),
         {'fields': [('url', 'duration'),
                     ('activity', 'slides'),
                     ('license')]}),
    ] + ELEMENT_FIELDSETS


@admin.register(Channel)
class ChannelAdmin(ElementAdmin):
    list_display = ('object_link', 'promoted', 'title', 'description', 'slug', 'creator', 'created', 'thumbnail', 'category')
    list_editable = ('promoted', 'title', 'description', 'slug', 'creator', 'created', 'thumbnail', 'category')
    list_display_links = None
    list_filter = (('creator', admin.RelatedOnlyFieldListFilter),
                   'category',
                   'promoted')
    search_fields = ('title',)

    form = make_ajax_form(Channel, {'creator': 'user',
                                    'contributor': 'user'})
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = [
        (_("Channel specific"), {'fields': ['category', 'syllabus']}),
    ] + ELEMENT_FIELDSETS


@admin.register(Chapter)
class ChapterAdmin(ElementAdmin):
    list_display = ('object_link', 'promoted', 'title', 'description', 'slug', 'creator', 'created', 'thumbnail', 'channel')
    list_editable = ('promoted', 'title', 'description', 'slug', 'creator', 'created', 'thumbnail', 'channel')
    list_display_links = None
    list_filter = (('creator', admin.RelatedOnlyFieldListFilter),
                   'channel', 'promoted')
    search_fields = ('title',)

    form = make_ajax_form(Chapter, {'channel': 'channel',
                                    'creator': 'user',
                                    'contributor': 'user'})
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        (None, {'fields': [('channel', 'teachers')]}),
    ] + ELEMENT_FIELDSETS


@admin.register(Activity)
class ActivityAdmin(ElementAdmin):
    list_display = ('object_link', 'promoted', 'title', 'description', 'slug', 'creator', 'created', 'thumbnail', 'chapter')
    list_editable = ('promoted', 'title', 'slug', 'description', 'creator', 'created', 'thumbnail', 'chapter')
    list_display_links = None
    list_filter = (('creator', admin.RelatedOnlyFieldListFilter),
                   'chapter', 'promoted')
    search_fields = ('title',)

    form = make_ajax_form(Activity, {'chapter': 'chapter',
                                     'creator': 'user',
                                     'contributor': 'user'})
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        (None, {'fields': ['chapter']}),
    ] + ELEMENT_FIELDSETS


def make_public(self, modeladmin, request, queryset):
    queryset.update(visibility=VISIBILITY_PUBLIC)
make_public.short_description = "Make selected annotations public"

def make_featured(self, modeladmin, request, queryset):
    queryset.update(featured=1)
make_featured.short_description = "Make selected annotations featured"


@admin.register(Annotation)
class AnnotationAdmin(ElementAdmin):
    list_display = ('object_link', 'promoted', 'begin', 'title', 'description', 'group', 'visibility', 'annotationtype', 'video_name', 'creator', 'created')
    list_editable = ('promoted', 'begin', 'title', 'description', 'group', 'visibility', 'annotationtype')
    list_display_links = None
    list_filter = (('annotationtype', admin.RelatedOnlyFieldListFilter),
                   ('group', admin.RelatedOnlyFieldListFilter),
                   ('video', admin.RelatedOnlyFieldListFilter),
                   'promoted',
                   ('creator', admin.RelatedOnlyFieldListFilter))
    search_fields = ('title', 'description',)
    actions = [ make_public, make_featured ]

    form = make_ajax_form(Annotation, {'video': 'video',
                                       'creator': 'user',
                                       'contributor': 'user'})
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        (None, {'fields': [('begin', 'end', 'video'),
                           ('annotationtype', 'group')]}),
    ] + USERCONTENT_FIELDSETS + ELEMENT_FIELDSETS

    def video_name(self, a):
        return a.video.title

@admin.register(AnnotationType)
class AnnotationTypeAdmin(ElementAdmin):
    list_display = ('pk', 'title', 'creator', 'created', 'annotation_count')
    list_editable = ('title',)
    list_display_links = ('pk',)
    list_filter = (('creator', admin.RelatedOnlyFieldListFilter),)
    search_fields = ('title',)

    def annotation_count(self, at):
        return at.annotation_set.count()

    form = make_ajax_form(AnnotationType, {'creator': 'user',
                                           'contributor': 'user'})
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [(None,               {'fields': [('slug', 'state')]}),
                 (_("Metadata"),      {'fields': [('creator', 'created', 'contributor', 'modified')], 'classes': ['collapse']}),
                 (_("Content"),       {'fields': [('title', 'thumbnail'), 'description']})]


@admin.register(Comment)
class CommentAdmin(ElementAdmin):
    list_display = ('pk', 'promoted', 'title', 'creator', 'created',)
    list_editable = ('promoted', 'title',)
    list_display_links = ('pk',)
    list_filter = (('creator', admin.RelatedOnlyFieldListFilter),
                   'promoted')
    search_fields = ('title',)

    form = make_ajax_form(Comment, {'creator': 'user',
                                    'contributor': 'user'})
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        (None, {'fields': ['group', ('parent_annotation', 'parent_video', 'parent_comment')]}),
    ] + USERCONTENT_FIELDSETS + ELEMENT_FIELDSETS

class UserInline(admin.TabularInline):
    model = Group.user_set.related.through
    extra = 0

class GroupMetadataInline(admin.StackedInline):
    model = GroupMetadata
    extra = 1
    form = make_ajax_form(GroupMetadata, {'creator': 'user',
                                         'contributor': 'user'})
    fieldsets = [
        (_("Metadata"),      {'fields': [('creator', 'created', 'contributor', 'modified')], 'classes': ['collapse']}),
        (_("Content"),       {'fields': [('title', 'thumbnail'), 'description']}),
    ]
GroupAdmin.inlines = [GroupMetadataInline, UserInline] + list(GroupAdmin.inlines)
GroupAdmin.search_fields = ('name', 'metadata__description')
GroupAdmin.user_count = lambda self, g: g.user_set.count()
GroupAdmin.annotation_count = lambda self, g: Annotation.objects.filter(group=g).count()
GroupAdmin.list_display = ('name', 'user_count', 'annotation_count')
def save_group_model(self, request, obj, form, change):
    if not getattr(obj.metadata, 'creator', None):
        obj.metadata.creator = request.user
    obj.metadata.contributor = request.user
    obj.metadata.modified = datetime.datetime.now()
    obj.save()
GroupAdmin.save_model = save_group_model

class UserMetadataInline(admin.StackedInline):
    model = UserMetadata
    fieldsets = [(None,       {'fields': [ ('thumbnail', 'description'), 'config' ]})]
UserAdmin.inlines = [UserMetadataInline] + list(UserAdmin.inlines)
UserAdmin.search_fields = ('username', 'metadata__description')

@admin.register(Newsitem)
class NewsitemAdmin(ElementAdmin):
    list_display = ('pk', 'title', 'title_en', 'description', 'description_en', 'published', 'creator', 'created',)
    list_editable = ('title', 'title_en', 'description', 'description_en')
    list_display_links = ('pk',)
    list_filter = (('creator', admin.RelatedOnlyFieldListFilter),)
    search_fields = ('title', 'description')

    form = make_ajax_form(Newsitem, {'creator': 'user',
                                     'contributor': 'user'})
    fieldsets = [(None,               {'fields': [('published', 'thumbnail'), ('title', 'title_en'), ('description', 'description_en'), 'slug']}),
                 (_("Metadata"),      {'fields': [('creator', 'created', 'contributor', 'modified')], 'classes': ['collapse']})]
