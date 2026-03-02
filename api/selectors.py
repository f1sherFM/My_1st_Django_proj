from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.request import Request

from blog.models import Post


def get_visible_post_or_404(request: Request, slug: str) -> Post:
    # В одном месте фиксируем policy видимости черновиков, чтобы не дублировать ее в нескольких views.
    post = get_object_or_404(
        Post.objects.select_related("author", "category"), slug=slug
    )
    if post.is_published:
        return post

    user = request.user
    if user.is_authenticated and (user.is_staff or user.id == post.author_id):
        return post

    raise Http404("Post not found")
