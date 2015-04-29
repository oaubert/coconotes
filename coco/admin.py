from django.contrib import admin
from .models import Course, Video, Module, License, Annotation, Comment, Resource, Newsitem

admin.site.register(Course)
admin.site.register(Video)
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
