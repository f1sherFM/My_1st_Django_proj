from django.urls import path

from .views import (
    CategoryCreateView,
    CategoryListView,
    CategoryPostListView,
    CommentCreateView,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostListView,
    PostUpdateView,
)

app_name = "blog"

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("category/create/", CategoryCreateView.as_view(), name="category_create"),
    path("category/<slug:slug>/", CategoryPostListView.as_view(), name="category_posts"),
    path("post/create/", PostCreateView.as_view(), name="post_create"),
    path("post/<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    path("post/<slug:slug>/edit/", PostUpdateView.as_view(), name="post_edit"),
    path("post/<slug:slug>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("post/<slug:slug>/comment/", CommentCreateView.as_view(), name="comment_create"),
]
