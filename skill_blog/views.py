from django.shortcuts import render


def permission_denied_view(request, exception):
    return render(request, "errors/403.html", status=403)


def page_not_found_view(request, exception):
    return render(request, "errors/404.html", status=404)
