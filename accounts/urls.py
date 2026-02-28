from django.urls import path

from .views import CustomLoginView, CustomLogoutView, ProfileDetailView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("profile/<str:username>/", ProfileDetailView.as_view(), name="profile"),
]
