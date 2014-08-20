from django.contrib import admin

# Register your models here.

class ElementAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title', )

    prepopulated_fields = {'slug': ('title', )}
