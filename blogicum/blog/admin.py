from django.contrib import admin

from .models import Location, Category, Post, Comment


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'is_published',
    )
    list_display_links = (
        'name',
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    search_fields = (
        'title',
        'slug'
    )
    list_filter = (
        'is_published',
    )
    list_display_links = (
        'title',
    )


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'is_published',
        'author',
        'location',
        'category',
        'created_at',
    )
    list_editable = (
        'is_published',
        'category',
    )
    search_fields = (
        'title',
        'author__username',
        'location__name',
    )
    list_filter = (
        'is_published',
        'category'
    )
    list_display_links = (
        'title',
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'post',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    search_fields = (
        'text',
        'author__username',
        'post__title',
    )
    list_filter = (
        'is_published',
    )
    list_display_links = (
        'text',
    )


admin.site.register(Location, LocationAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)

admin.site.empty_value_display = 'Не задано'
