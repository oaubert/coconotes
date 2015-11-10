from django.contrib import admin
from .models import Course, Video, Module, License, AnnotationType, Annotation, Comment, Resource, Newsitem, Activity

admin.site.register(License)
admin.site.register(Resource)
admin.site.register(Comment)
admin.site.register(Newsitem)
admin.site.register(AnnotationType)

class CreatorMixin(object):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        obj.contributor = request.user
        obj.save()

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

@admin.register(Course)
class CourseAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'creator', 'created', 'thumbnail', 'category')
    list_editable = ('title', 'slug', 'creator', 'created', 'thumbnail', 'category')
    list_display_links = ('pk', )
    list_filter = ( 'creator', 'category' )
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}

@admin.register(Module)
class ModuleAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'creator', 'created', 'thumbnail', 'course')
    list_editable = ('title', 'slug', 'creator', 'created', 'thumbnail', 'course')
    list_display_links = ('pk', )
    list_filter = ( 'creator', 'course' )
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}

@admin.register(Activity)
class ActivityAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'creator', 'created', 'thumbnail', 'module')
    list_editable = ('title', 'slug', 'creator', 'created', 'thumbnail', 'module')
    list_display_links = ('pk', )
    list_filter = ( 'creator', 'module' )
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}

@admin.register(Annotation)
class AnnotationAdmin(CreatorMixin, admin.ModelAdmin):
    list_display = ('pk', 'title', 'creator', 'created', )
    list_editable = ('title', )
    list_display_links = ('pk', )
    list_filter = ( 'creator', )
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}
