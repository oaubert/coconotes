from django.contrib import admin
from .models import Course, Video, Module, License, Annotation, Comment, Resource, Newsitem, Activity

admin.site.register(License)
admin.site.register(Annotation)
admin.site.register(Resource)
admin.site.register(Comment)
admin.site.register(Newsitem)

# Register your models here.

class ElementAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'shorttitle', 'package_id', 'slug', 'creator', 'created', 'activity', 'thumbnail')
    list_editable = ('title', 'shorttitle', 'package_id', 'slug', 'creator', 'created', 'activity', 'thumbnail')
    list_display_links = ('pk', )
    list_filter = ( 'creator', )
    search_fields = ('title', 'shorttitle', 'package_id')

    prepopulated_fields = {'slug': ('title', )}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'shorttitle', 'slug', 'creator', 'created', 'thumbnail', 'category')
    list_editable = ('title', 'shorttitle', 'slug', 'creator', 'created', 'thumbnail', 'category')
    list_display_links = ('pk', )
    list_filter = ( 'creator', 'category' )
    search_fields = ('title', 'shorttitle')

    prepopulated_fields = {'slug': ('title', )}

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'shorttitle', 'slug', 'creator', 'created', 'thumbnail', 'course')
    list_editable = ('title', 'shorttitle', 'slug', 'creator', 'created', 'thumbnail', 'course')
    list_display_links = ('pk', )
    list_filter = ( 'creator', 'course' )
    search_fields = ('title', 'shorttitle')

    prepopulated_fields = {'slug': ('title', )}

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'shorttitle', 'slug', 'creator', 'created', 'thumbnail', 'module')
    list_editable = ('title', 'shorttitle', 'slug', 'creator', 'created', 'thumbnail', 'module')
    list_display_links = ('pk', )
    list_filter = ( 'creator', 'module' )
    search_fields = ('title', 'shorttitle')

    prepopulated_fields = {'slug': ('title', )}
