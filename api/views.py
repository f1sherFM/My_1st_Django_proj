from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from blog.models import Category, Comment, Post

from .permissions import IsAuthorOrStaff
from .serializers import (
    CategorySerializer,
    CommentApproveSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostWriteSerializer,
)


def _check_post_visibility_or_404(post, user):
    # Черновики не должны раскрывать факт существования для чужих пользователей.
    if post.is_published:
        return

    if user.is_authenticated and (user.is_staff or user.id == post.author_id):
        return

    raise Http404("Post not found")


class PostListCreateAPIView(generics.ListCreateAPIView):
    queryset = Post.objects.select_related("author", "category").order_by("-created_at")
    search_fields = ("title", "content")

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PostListSerializer
        return PostWriteSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.select_related("author", "category")
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return PostDetailSerializer
        return PostWriteSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAuthorOrStaff()]

    def get_object(self):
        post = get_object_or_404(self.get_queryset(), slug=self.kwargs["slug"])
        _check_post_visibility_or_404(post, self.request.user)
        self.check_object_permissions(self.request, post)
        return post


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryPostsListAPIView(generics.ListAPIView):
    serializer_class = PostListSerializer
    search_fields = ("title", "content")

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return Post.objects.filter(category=category, is_published=True).select_related("author", "category").order_by(
            "-created_at"
        )


class PostCommentsListCreateAPIView(generics.ListCreateAPIView):
    search_fields = ()

    def get_post(self):
        post = get_object_or_404(Post.objects.select_related("author", "category"), slug=self.kwargs["slug"])
        _check_post_visibility_or_404(post, self.request.user)
        return post

    def get_queryset(self):
        post = self.get_post()
        return post.comments.filter(is_approved=True).select_related("author").order_by("created_at")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CommentSerializer
        return CommentCreateSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        post = self.get_post()
        # Комментарии в API идут через премодерацию так же, как и в HTML части.
        serializer.save(author=self.request.user, post=post, is_approved=False)


class CommentApproveAPIView(generics.UpdateAPIView):
    queryset = Comment.objects.select_related("author", "post")
    serializer_class = CommentApproveSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ["patch", "options"]
