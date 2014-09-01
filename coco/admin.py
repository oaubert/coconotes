from django.contrib import admin
from .models import Course, Video, Module, License, Annotation, Comment

admin.site.register(Course)
admin.site.register(Video)
admin.site.register(License)
admin.site.register(Annotation)
admin.site.register(Comment)

# Register your models here.

class ElementAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}
