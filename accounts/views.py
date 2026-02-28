from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView

from .forms import UserRegisterForm
from .models import User


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("blog:post_list")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = "registration/login.html"


class CustomLogoutView(LogoutView):
    # LogoutView в Django принимает POST, это безопаснее, чем GET-логаут.
    next_page = reverse_lazy("blog:post_list")


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/profile_detail.html"
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        return get_object_or_404(User.objects.select_related("profile"), username=self.kwargs["username"])
