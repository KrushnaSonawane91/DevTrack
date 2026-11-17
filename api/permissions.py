
from rest_framework.permissions import BasePermission, SAFE_METHODS


class CanManageIssue(BasePermission):
    """
    All authenticated users can view issues.
    Only the reporter, project owner, or superuser
    can update or delete an issue.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_superuser
            or obj.reporter_id == request.user.id
            or obj.project.owner_id == request.user.id
        )
