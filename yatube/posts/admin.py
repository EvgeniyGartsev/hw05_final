from django.contrib import admin

from .models import Post, Group, Comment, Follow


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


class CommentAdmin(admin.ModelAdmin):
    '''Manage groups in admin panel'''
    list_display = ("pk", "post", "author", "text")
    search_fields = ("author", "post")
    list_filter = ("text",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    '''Manage groups in admin panel'''
    list_display = ("pk", "user", "author")
    search_fields = ("user",)
    list_filter = ("author",)
    empty_value_display = "-пусто-"


# register models in admin
# for access this models from admin
admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
