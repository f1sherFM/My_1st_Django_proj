from django import get_version
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from blog.models import Category, Comment, Post

from .permissions import IsAuthorOrStaff
from .selectors import get_visible_post_or_404
from .serializers import (
    CategorySerializer,
    CommentApproveSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    MeSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostWriteSerializer,
)


class PostListCreateAPIView(generics.ListCreateAPIView):
    queryset = Post.objects.select_related("author", "category").order_by("-created_at")
    search_fields = ("title", "content")

    def get_queryset(self) -> QuerySet[Post]:
        return super().get_queryset().filter(is_published=True)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PostListSerializer
        return PostWriteSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer: PostWriteSerializer) -> None:
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

    def get_object(self) -> Post:
        post = get_visible_post_or_404(self.request, self.kwargs["slug"])
        self.check_object_permissions(self.request, post)
        return post


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryPostsListAPIView(generics.ListAPIView):
    serializer_class = PostListSerializer
    search_fields = ("title", "content")

    def get_queryset(self) -> QuerySet[Post]:
        category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return (
            Post.objects.filter(category=category, is_published=True)
            .select_related("author", "category")
            .order_by("-created_at")
        )


class PostCommentsListCreateAPIView(generics.ListCreateAPIView):
    search_fields = ()

    def get_post(self) -> Post:
        return get_visible_post_or_404(self.request, self.kwargs["slug"])

    def get_queryset(self) -> QuerySet[Comment]:
        post = self.get_post()
        return (
            post.comments.filter(is_approved=True)
            .select_related("author")
            .order_by("created_at")
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CommentSerializer
        return CommentCreateSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer: CommentCreateSerializer) -> None:
        post = self.get_post()
        # Комментарии идут через премодерацию, чтобы API и HTML-часть вели себя одинаково безопасно.
        serializer.save(author=self.request.user, post=post, is_approved=False)


class CommentApproveAPIView(generics.UpdateAPIView):
    queryset = Comment.objects.select_related("author", "post")
    serializer_class = CommentApproveSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ["patch", "options"]

    def perform_update(self, serializer: CommentApproveSerializer) -> None:
        # Эндпоинт approve не доверяет входному body и всегда принудительно одобряет комментарий.
        serializer.save()


class MeAPIView(generics.RetrieveAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user


class HealthAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: Request) -> Response:
        # Простой health endpoint удобен для smoke-check и мониторинга без доступа к приватным данным.
        return Response({"status": "ok", "django": get_version(), "app": "skill_blog"})
