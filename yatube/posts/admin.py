from django.contrib import admin

from .models import Comment, Follow, Group, Post

admin.site.register(Group)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group', 'image',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'post')
    list_editable = ('text',)
    search_fields = ('text',)
    list_filter = ('author',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author',)
    list_editable = ('author',)
    search_fields = ('user',)
    list_filter = ('author',)
