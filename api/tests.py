
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from project_manager.models import Project
from issues.models import Issue, IssueComment


User = get_user_model()


class IssueAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.owner = User.objects.create_user(
            username="project_owner",
            password="TestPass123!"
        )
        self.member = User.objects.create_user(
            username="project_member",
            password="TestPass123!"
        )
        self.other_user = User.objects.create_user(
            username="other_user",
            password="TestPass123!"
        )

        self.project = Project.objects.create(
            name="API Test Project",
            description="Project for API testing",
            owner=self.owner
        )
        self.project.members.add(self.member)

        self.issue = Issue.objects.create(
            title="Login Bug",
            description="Login page is not working",
            project=self.project,
            reporter=self.owner,
            assignee=self.member,
            status="OPEN",
            priority="HIGH",
            issue_type="BUG"
        )

    # Authentication tests

    def test_unauthenticated_user_cannot_access_issues(self):
        response = self.client.get("/api/issues/")
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_view_issues(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get("/api/issues/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    # Issue creation tests

    def test_project_member_can_create_issue(self):
        self.client.force_authenticate(user=self.member)

        data = {
            "title": "API Created Issue",
            "description": "Created through REST API",
            "project": self.project.id,
            "assignee": self.member.id,
            "status": "OPEN",
            "priority": "MEDIUM",
            "issue_type": "TASK"
        }

        response = self.client.post(
            "/api/issues/", data, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Issue.objects.filter(title="API Created Issue").exists()
        )

    def test_user_cannot_create_issue_in_unrelated_project(self):
        unrelated_project = Project.objects.create(
            name="Unrelated Project",
            description="Not accessible",
            owner=self.other_user
        )

        self.client.force_authenticate(user=self.member)

        data = {
            "title": "Unauthorized Issue",
            "description": "Should not be created",
            "project": unrelated_project.id,
            "status": "OPEN",
            "priority": "LOW",
            "issue_type": "BUG"
        }

        response = self.client.post(
            "/api/issues/", data, format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            Issue.objects.filter(title="Unauthorized Issue").exists()
        )

    # Update permission tests

    def test_reporter_can_update_issue(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            f"/api/issues/{self.issue.id}/",
            {"title": "Updated Login Bug"},
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.title, "Updated Login Bug")

    def test_unrelated_user_cannot_update_issue(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f"/api/issues/{self.issue.id}/",
            {"title": "Unauthorized Update"},
            format="json"
        )

        self.assertEqual(response.status_code, 403)

    # Filtering tests

    def test_search_filter(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get("/api/issues/?search=Login")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Login Bug")

    def test_status_filter(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get("/api/issues/?status=OPEN")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_priority_filter(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get("/api/issues/?priority=HIGH")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_issue_type_filter(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get("/api/issues/?issue_type=BUG")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    # Comment API tests

    def test_user_can_view_issue_comments(self):
        IssueComment.objects.create(
            issue=self.issue,
            author=self.owner,
            body="Testing API comments"
        )

        self.client.force_authenticate(user=self.member)

        response = self.client.get(
            f"/api/issues/{self.issue.id}/comments/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["body"],
            "Testing API comments"
        )

    def test_authenticated_user_can_add_comment(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.post(
            f"/api/issues/{self.issue.id}/comments/",
            {"body": "Comment added through API"},
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            IssueComment.objects.filter(
                issue=self.issue,
                author=self.member,
                body="Comment added through API"
            ).exists()
        )

    # Dashboard test

    def test_dashboard_returns_statistics(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.get("/api/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_issues"], 1)
        self.assertEqual(response.data["open_issues"], 1)
        self.assertEqual(response.data["high_priority"], 1)
        self.assertEqual(response.data["total_projects"], 1)

    # Sorting test

    def test_issues_can_be_sorted_by_title(self):
        Issue.objects.create(
            title="Account Bug",
            description="Account issue",
            project=self.project,
            reporter=self.owner,
            status="OPEN",
            priority="LOW",
            issue_type="BUG"
        )

        self.client.force_authenticate(user=self.member)

        response = self.client.get(
            "/api/issues/?ordering=title"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data[0]["title"],
            "Account Bug"
        )
        self.assertEqual(
            response.data[1]["title"],
            "Login Bug"
        )
