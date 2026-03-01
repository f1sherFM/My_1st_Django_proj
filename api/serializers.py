from django.utils.text import slugify
from rest_framework import serializers

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

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class PostWriteSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Post
        fields = ("title", "slug", "content", "category", "is_published")

    def validate_slug(self, value):
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

    def validate_text(self, value):
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise serializers.ValidationError("Комментарий должен содержать минимум 3 символа.")
        return cleaned


class CommentApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "is_approved")
        read_only_fields = ("id", "is_approved")

    def update(self, instance, validated_data):
        instance.is_approved = True
        instance.save(update_fields=["is_approved"])
        return instance
