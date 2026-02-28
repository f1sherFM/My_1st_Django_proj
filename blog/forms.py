from django import forms
from django.utils.text import slugify

from .models import Category, Comment, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Явно сортируем категории, чтобы в форме был стабильный и удобный порядок выбора.
        category_queryset = Category.objects.order_by("name")
        self.fields["category"].queryset = category_queryset
        self.no_categories = not category_queryset.exists()

    class Meta:
        model = Post
        fields = ("title", "slug", "content", "category", "is_published")
        widgets = {
            "content": forms.Textarea(attrs={"rows": 8}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        if not slug:
            return ""
        return slugify(slug)[:200]

    def clean(self):
        cleaned_data = super().clean()
        if self.no_categories:
            raise forms.ValidationError("Сначала создайте хотя бы одну категорию.")
        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        # Минимальная длина отсеивает пустые/шумовые комментарии еще до модерации.
        if len(text) < 3:
            raise forms.ValidationError("Комментарий должен содержать минимум 3 символа.")
        return text


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "slug")

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        if not slug:
            return ""
        return slugify(slug)[:120]
