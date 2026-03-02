from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from blog.models import Post


class IsAuthorOrStaff(BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Post) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            obj.author_id == request.user.id or request.user.is_staff
        )
