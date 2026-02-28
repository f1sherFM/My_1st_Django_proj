from django import forms
from django.utils.text import slugify

from .models import Comment, Post


class PostForm(forms.ModelForm):
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
