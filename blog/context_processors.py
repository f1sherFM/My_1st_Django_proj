from .models import Category


def navigation_categories(request):
    return {"navigation_categories": Category.objects.all()}
