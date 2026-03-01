from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    CategoryListAPIView,
    CategoryPostsListAPIView,
    CommentApproveAPIView,
    PostCommentsListCreateAPIView,
    PostListCreateAPIView,
    PostRetrieveUpdateDestroyAPIView,
)

app_name = "api"

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("posts/", PostListCreateAPIView.as_view(), name="post_list_create"),
    path("posts/<slug:slug>/", PostRetrieveUpdateDestroyAPIView.as_view(), name="post_detail"),
    path("categories/", CategoryListAPIView.as_view(), name="category_list"),
    path("categories/<slug:slug>/posts/", CategoryPostsListAPIView.as_view(), name="category_posts"),
    path("posts/<slug:slug>/comments/", PostCommentsListCreateAPIView.as_view(), name="post_comments"),
    path("comments/<int:pk>/approve/", CommentApproveAPIView.as_view(), name="comment_approve"),
]
