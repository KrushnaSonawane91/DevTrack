
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers

from issues.models import Issue, IssueComment
from project_manager.models import Project

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(
        source="owner.username",
        read_only=True
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "owner_username",
            "members",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "created_at",
            "updated_at",
        ]


class IssueCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source="author.username",
        read_only=True
    )

    class Meta:
        model = IssueComment
        fields = [
            "id",
            "issue",
            "author",
            "author_username",
            "body",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "issue",
            "author",
            "created_at",
            "updated_at",
        ]


class IssueSerializer(serializers.ModelSerializer):
    reporter_username = serializers.CharField(
        source="reporter.username",
        read_only=True
    )

    assignee_username = serializers.CharField(
        source="assignee.username",
        read_only=True
    )

    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )

    comments = IssueCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "project",
            "project_name",
            "reporter",
            "reporter_username",
            "assignee",
            "assignee_username",
            "status",
            "priority",
            "issue_type",
            "comments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reporter",
            "reporter_username",
            "project_name",
            "assignee_username",
            "created_at",
            "updated_at",
            "comments",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user is None or not user.is_authenticated:
            allowed_projects = Project.objects.none()

        elif user.is_superuser:
            allowed_projects = Project.objects.all()

        else:
            allowed_projects = Project.objects.filter(
                Q(owner=user) | Q(members=user)
            )

        if isinstance(self.instance, Issue):
            allowed_projects = allowed_projects | Project.objects.filter(
                pk=self.instance.project_id
            )

        self.fields["project"].queryset = allowed_projects.distinct()

        self.fields["assignee"].queryset = User.objects.filter(
            is_active=True
        ).order_by("username")

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Issue title is required."
            )

        return value


class DashboardSerializer(serializers.Serializer):
    total_issues = serializers.IntegerField()
    open_issues = serializers.IntegerField()
    in_progress_issues = serializers.IntegerField()
    resolved_issues = serializers.IntegerField()
    closed_issues = serializers.IntegerField()
    low_priority = serializers.IntegerField()
    medium_priority = serializers.IntegerField()
    high_priority = serializers.IntegerField()
    critical_priority = serializers.IntegerField()
    total_projects = serializers.IntegerField()
