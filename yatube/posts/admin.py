from django.contrib import admin

from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    '''Manage posts in admin panel'''
    list_display = ("pk", "text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    '''Manage groups in admin panel'''
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title",)
    list_filter = ("title",)
    empty_value_display = "-пусто-"


# register models in admin
# for access this models from admin
admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
