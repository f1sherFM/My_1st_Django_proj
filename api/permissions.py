from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (obj.author_id == request.user.id or request.user.is_staff)
