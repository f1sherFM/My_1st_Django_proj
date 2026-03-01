from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from blog.views import CategoryCreateView

# Кастомные handlers нужны, чтобы 403/404 выглядели единообразно с UI проекта.
handler403 = "skill_blog.views.permission_denied_view"
handler404 = "skill_blog.views.page_not_found_view"

urlpatterns = [
    path("admin/", admin.site.urls),
    # Совместимость со старыми шаблонами без namespace: {% url 'category_create' %}.
    path("category/create/", CategoryCreateView.as_view(), name="category_create"),
    path("api/", include("api.urls")),
    path("", include("accounts.urls")),
    path("", include("blog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
