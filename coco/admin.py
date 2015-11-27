from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Course, Video, Module, License, AnnotationType, Annotation, Comment, Resource, Newsitem, Activity

admin.site.register(License)
admin.site.register(Resource)
admin.site.register(Newsitem)

class CreatorMixin(object):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        obj.contributor = request.user
        obj.save()

# Common fieldsets for all Elements
ELEMENT_FIELDSETS = [
    (None,               {'fields': [ ('slug', 'state') ] }),
    (_("Metadata"),      {'fields': [ ('creator', 'created', 'contributor', 'modified') ], 'classes': ['collapse']}),
    (_("Content"),       {'fields': [ ('title', 'thumbnail'), 'description' ]}),
    (_("Tags"),         {'fields': [ 'tags' ] })
]
USERCONTENT_FIELDSETS = [
    (_("User content"), {'fields': [ ('visibility', 'contenttype'),
                                     'contentdata' ]}),
]

class ElementAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}

@admin.register(Video)
class VideoAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'creator', 'duration', 'created', 'thumbnail')
    list_editable = ('title', 'slug', 'creator', 'duration', 'thumbnail')
    list_display_links = ('pk', )
    list_filter = ( 'creator', )
    search_fields = ('title', 'slug')

    prepopulated_fields = {'slug': ('title', )}
    fieldsets = [
                (_("Video specific"), {'fields': [ ('url', 'duration'),
                                                   ('activity', 'slides'),
                                                   ('license', 'package_id') ] }),
    ] + ELEMENT_FIELDSETS

@admin.register(Course)
class CourseAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'creator', 'created', 'thumbnail', 'category')
    list_editable = ('title', 'slug', 'creator', 'created', 'thumbnail', 'category')
    list_display_links = ('pk', )
    list_filter = ( 'creator', 'category' )
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}

    fieldsets = [
        (_("Course specific"), {'fields': [ 'category', 'syllabus' ] }),
    ] + ELEMENT_FIELDSETS

@admin.register(Module)
class ModuleAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'creator', 'created', 'thumbnail', 'course')
    list_editable = ('title', 'slug', 'creator', 'created', 'thumbnail', 'course')
    list_display_links = ('pk', )
    list_filter = ( 'creator', 'course' )
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}
    fieldsets = [
        (None, {'fields': [ ('course', 'teachers') ] }),
    ] + ELEMENT_FIELDSETS


@admin.register(Activity)
class ActivityAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'creator', 'created', 'thumbnail', 'module')
    list_editable = ('title', 'slug', 'creator', 'created', 'thumbnail', 'module')
    list_display_links = ('pk', )
    list_filter = ( 'creator', 'module' )
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}
    fieldsets = [
        (None, {'fields': [ 'module' ] }),
    ] + ELEMENT_FIELDSETS

@admin.register(Annotation)
class AnnotationAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('pk', 'title', 'creator', 'created', )
    list_editable = ('title', )
    list_display_links = ('pk', )
    list_filter = ( 'creator', )
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}
    fieldsets = [
        (None, {'fields': [ ('begin', 'end', 'video'),
                            ('annotationtype', 'group') ] }),
    ] + USERCONTENT_FIELDSETS + ELEMENT_FIELDSETS

@admin.register(AnnotationType)
class AnnotationTypeAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('pk', 'title', 'creator', 'created', )
    list_editable = ('title', )
    list_display_links = ('pk', )
    list_filter = ( 'creator', )
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}
    fieldsets = [ (None,               {'fields': [ ('slug', 'state') ] }),
                  (_("Metadata"),      {'fields': [ ('creator', 'created', 'contributor', 'modified') ], 'classes': ['collapse']}),
                  (_("Content"),       {'fields': [ ('title', 'thumbnail'), 'description' ]}) ]

@admin.register(Comment)
class CommentAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('pk', 'title', 'creator', 'created', )
    list_editable = ('title', )
    list_display_links = ('pk', )
    list_filter = ( 'creator', )
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}
    fieldsets = [
        (None, {'fields': [ 'group', ('parent_annotation', 'parent_video', 'parent_comment') ] }),
    ] + USERCONTENT_FIELDSETS + ELEMENT_FIELDSETS
