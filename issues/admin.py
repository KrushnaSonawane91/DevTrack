
from django.contrib import admin
from .models import Issue


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "reporter",
        "assignee",
        "status",
        "priority",
        "issue_type",
        "created_at",
    )

    list_filter = ("status", "priority", "issue_type", "created_at")
    search_fields = ("title", "description")
    list_select_related = ("project", "reporter", "assignee")
