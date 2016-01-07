from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin, UserAdmin

from ajax_select.admin import AjaxSelectAdmin
from ajax_select.helpers import make_ajax_form

from .models import Channel, Video, Chapter, License, AnnotationType, Annotation, Comment, Resource, Newsitem, Activity
from .models import UserMetadata, GroupMetadata

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

    list_display = ('title', 'slug', 'promoted')
    search_fields = ('title',)

    prepopulated_fields = {'slug': ('title',)}
    list_select_related = True

    def object_link(self, item):
        try:
            return u'<a target="_blank" href="{absurl}">\u25ce</a> <a target="_blank" href="{url}">\u21eb</a>'.format(absurl=item.get_absolute_url(), url=item.url)
        except AttributeError:
            return u'<a target="_blank" href="{absurl}">\u25ce</a>'.format(absurl=item.get_absolute_url())
    object_link.short_description = 'View'
    object_link.allow_tags = True


@admin.register(Video)
class VideoAdmin(ElementAdmin):
    list_display = ('pk', 'object_link', 'promoted', 'title', 'slug', 'creator', 'duration', 'created', 'thumbnail')
    list_editable = ('promoted', 'title', 'slug', 'creator', 'duration', 'thumbnail')
    list_display_links = ('pk',)
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
    list_display = ('pk', 'object_link', 'promoted', 'title', 'slug', 'creator', 'created', 'thumbnail', 'category')
    list_editable = ('promoted', 'title', 'slug', 'creator', 'created', 'thumbnail', 'category')
    list_display_links = ('pk',)
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
    list_display = ('pk', 'object_link', 'promoted', 'title', 'slug', 'creator', 'created', 'thumbnail', 'channel')
    list_editable = ('promoted', 'title', 'slug', 'creator', 'created', 'thumbnail', 'channel')
    list_display_links = ('pk',)
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
    list_display = ('pk', 'object_link', 'promoted', 'title', 'slug', 'creator', 'created', 'thumbnail', 'chapter')
    list_editable = ('promoted', 'title', 'slug', 'creator', 'created', 'thumbnail', 'chapter')
    list_display_links = ('pk',)
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


@admin.register(Annotation)
class AnnotationAdmin(ElementAdmin):
    list_display = ('pk', 'object_link', 'promoted', 'begin', 'title', 'description', 'annotationtype', 'group', 'video_name', 'creator', 'created',)
    list_editable = ('promoted', 'begin', 'title', 'description', 'group', 'annotationtype')
    list_display_links = ('pk',)
    list_filter = (('annotationtype', admin.RelatedOnlyFieldListFilter),
                   ('group', admin.RelatedOnlyFieldListFilter),
                   ('video', admin.RelatedOnlyFieldListFilter),
                   'promoted',
                   ('creator', admin.RelatedOnlyFieldListFilter))
    search_fields = ('title', 'description',)

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
    list_display = ('pk', 'title', 'creator', 'created',)
    list_editable = ('title',)
    list_display_links = ('pk',)
    list_filter = (('creator', admin.RelatedOnlyFieldListFilter),)
    search_fields = ('title',)

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

class UserMetadataInline(admin.StackedInline):
    model = UserMetadata
    fieldsets = [(None,       {'fields': [ ('thumbnail', 'description') ]})]
UserAdmin.inlines = [UserMetadataInline] + list(UserAdmin.inlines)
UserAdmin.search_fields = ('username', 'metadata__description')

@admin.register(Newsitem)
class NewsitemAdmin(ElementAdmin):
    list_display = ('pk', 'title', 'description', 'published', 'creator', 'created',)
    list_editable = ('title', 'description', 'published')
    list_display_links = ('pk',)
    list_filter = (('creator', admin.RelatedOnlyFieldListFilter),)
    search_fields = ('title', 'description')

    form = make_ajax_form(Newsitem, {'creator': 'user',
                                     'contributor': 'user'})
    fieldsets = [(None,               {'fields': [('published'), ('title', 'thumbnail'), 'description', 'slug']}),
                 (_("Metadata"),      {'fields': [('creator', 'created', 'contributor', 'modified')], 'classes': ['collapse']})]
