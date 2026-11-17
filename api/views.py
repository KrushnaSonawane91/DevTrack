
from django.db.models import Q
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from issues.models import Issue, IssueComment
from project_manager.models import Project

from .permissions import CanManageIssue
from .serializers import (
    IssueSerializer,
    IssueCommentSerializer,
    ProjectSerializer,
    DashboardSerializer,
)


@extend_schema_view(
    list=extend_schema(operation_id="issues_list"),
    retrieve=extend_schema(operation_id="issue_retrieve"),
)
class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, CanManageIssue]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Issue.objects.none()

        queryset = Issue.objects.select_related(
            "project", "reporter", "assignee"
        ).prefetch_related("comments")

        search = self.request.query_params.get("search")
        status = self.request.query_params.get("status")
        priority = self.request.query_params.get("priority")
        issue_type = self.request.query_params.get("issue_type")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        if issue_type:
            queryset = queryset.filter(issue_type=issue_type)

        ordering = self.request.query_params.get(
            "ordering", "-created_at"
        )

        allowed_ordering = [
            "created_at",
            "-created_at",
            "updated_at",
            "-updated_at",
            "title",
            "-title",
        ]

        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class ProjectListAPIView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Project.objects.all().order_by("name")

        return Project.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct().order_by("name")


class IssueCommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = IssueCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return IssueComment.objects.filter(
            issue_id=self.kwargs["issue_id"]
        ).select_related("author").order_by("created_at")

    def perform_create(self, serializer):
        issue = generics.get_object_or_404(
            Issue,
            pk=self.kwargs["issue_id"]
        )

        serializer.save(
            issue=issue,
            author=self.request.user
        )


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=DashboardSerializer)
    def get(self, request):
        issues = Issue.objects.all()

        data = {
            "total_issues": issues.count(),
            "open_issues": issues.filter(status="OPEN").count(),
            "in_progress_issues": issues.filter(
                status="IN_PROGRESS"
            ).count(),
            "resolved_issues": issues.filter(
                status="RESOLVED"
            ).count(),
            "closed_issues": issues.filter(status="CLOSED").count(),
            "low_priority": issues.filter(priority="LOW").count(),
            "medium_priority": issues.filter(
                priority="MEDIUM"
            ).count(),
            "high_priority": issues.filter(priority="HIGH").count(),
            "critical_priority": issues.filter(
                priority="CRITICAL"
            ).count(),
            "total_projects": Project.objects.filter(
                Q(owner=request.user) | Q(members=request.user)
            ).distinct().count()
            if not request.user.is_superuser
            else Project.objects.count(),
        }

        return Response(data)
