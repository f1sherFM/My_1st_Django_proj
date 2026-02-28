from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Автослаг для категории нужен, чтобы пользователь мог создать ее без ручного ввода slug.
        if not self.slug:
            self.slug = self._build_unique_slug()
        super().save(*args, **kwargs)

    def _build_unique_slug(self):
        base_slug = (slugify(self.name) or "category")[:120]
        candidate = base_slug
        counter = 2

        while Category.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
            suffix = f"-{counter}"
            trimmed_base = base_slug[: 120 - len(suffix)]
            candidate = f"{trimmed_base}{suffix}"
            counter += 1

        return candidate


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="posts")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Автослаг снижает количество ручных ошибок, а суффиксы решают коллизии без падений.
        if not self.slug:
            self.slug = self._build_unique_slug()
        super().save(*args, **kwargs)

    def _build_unique_slug(self):
        base_slug = slugify(self.title) or "post"
        base_slug = base_slug[:200]
        candidate = base_slug
        counter = 2

        while Post.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
            suffix = f"-{counter}"
            trimmed_base = base_slug[: 200 - len(suffix)]
            candidate = f"{trimmed_base}{suffix}"
            counter += 1

        return candidate


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Комментарий от {self.author} к {self.post}"
