from typing import Any

from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.request import Request

from accounts.models import User
from blog.models import Category, Comment, Post


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "slug")


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Post
        fields = ("slug", "title", "author", "category", "created_at")


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "slug",
            "title",
            "author",
            "category",
            "category_slug",
            "created_at",
            "updated_at",
            "content",
            "comments_count",
        )

    def get_comments_count(self, obj: Post) -> int:
        return obj.comments.filter(is_approved=True).count()


class PostWriteSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Post
        fields = ("title", "slug", "content", "category", "is_published")

    def validate_slug(self, value: str) -> str:
        raw_slug = (value or "").strip()
        if not raw_slug:
            return ""
        # Если slug передан клиентом, нормализуем его; коллизии финально решит модель.
        return slugify(raw_slug)[:200]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "text", "created_at")


class CommentCreateSerializer(serializers.ModelSerializer):
    text = serializers.CharField(min_length=3)

    class Meta:
        model = Comment
        fields = ("text",)

    def validate_text(self, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise serializers.ValidationError(
                "Комментарий должен содержать минимум 3 символа."
            )
        return cleaned


class CommentApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "is_approved")
        read_only_fields = ("id", "is_approved")

    def update(self, instance: Comment, validated_data: dict[str, Any]) -> Comment:
        instance.is_approved = True
        instance.save(update_fields=["is_approved"])
        return instance


class MeSerializer(serializers.ModelSerializer):
    bio = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("username", "email", "is_staff", "bio", "avatar")

    def get_bio(self, obj: User) -> str:
        profile = getattr(obj, "profile", None)
        return profile.bio if profile else ""

    def get_avatar(self, obj: User) -> str | None:
        profile = getattr(obj, "profile", None)
        if not profile or not profile.avatar:
            return None

        request = self.context.get("request")
        if isinstance(request, Request):
            return request.build_absolute_uri(profile.avatar.url)

        return profile.avatar.url
