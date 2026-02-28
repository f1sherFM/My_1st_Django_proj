from django.contrib import admin

from .models import Category, Comment, Post


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("author", "text", "is_approved", "created_at")
    readonly_fields = ("created_at",)


@admin.action(description="Approve comments")
def approve_comments(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "is_published", "created_at")
    list_filter = ("is_published", "category", "created_at")
    search_fields = ("title", "content", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CommentInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("post__title", "author__username", "text")
    actions = [approve_comments]
