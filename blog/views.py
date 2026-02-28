from django.core.exceptions import PermissionDenied
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(is_published=True).select_related("author", "category")
        query = self.request.GET.get("q", "").strip()

        # Поиск активируется только на осмысленном запросе, иначе ведем себя как обычный список.
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query)).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        return context


class CategoryListView(ListView):
    model = Category
    template_name = "blog/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.annotate(
            published_posts_count=Count("posts", filter=Q(posts__is_published=True))
        )


class CategoryPostListView(ListView):
    model = Post
    template_name = "blog/category_posts.html"
    context_object_name = "posts"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(Category, slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Post.objects.filter(is_published=True, category=self.category)
            .select_related("author", "category")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        approved_comments = Comment.objects.filter(is_approved=True).select_related("author")
        return Post.objects.filter(is_published=True).select_related("author", "category").prefetch_related(
            Prefetch("comments", queryset=approved_comments)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        context["approved_comments"] = self.object.comments.all()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author_id == self.request.user.id

    def handle_no_permission(self):
        # Неавторизованный пользователь должен попасть на login, авторизованный не-автор — получить 403.
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("blog:post_list")


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug, is_published=True)
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            # Премодерация защищает от спама и случайно токсичного контента.
            comment.is_approved = False
            comment.save()

        return redirect("blog:post_detail", slug=slug)
