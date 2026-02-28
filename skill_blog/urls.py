from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Кастомные handlers нужны, чтобы 403/404 выглядели единообразно с UI проекта.
handler403 = "skill_blog.views.permission_denied_view"
handler404 = "skill_blog.views.page_not_found_view"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("", include("blog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
