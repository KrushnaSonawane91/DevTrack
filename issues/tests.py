
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from issues.models import Issue, IssueActivity, IssueComment
from project_manager.models import Project


User = get_user_model()


class DevTrackIssueTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="projectowner",
            password="TestPass123!",
        )
        self.reporter = User.objects.create_user(
            username="reporter",
            password="TestPass123!",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="TestPass123!",
        )

        self.project = Project.objects.create(
            name="Test Project",
            description="Project for automated tests",
            owner=self.owner,
        )
        self.project.members.add(self.reporter)

        self.issue = Issue.objects.create(
            title="Login page bug",
            description="Login fails with valid credentials",
            project=self.project,
            reporter=self.reporter,
            status=Issue.Status.OPEN,
            priority=Issue.Priority.HIGH,
            issue_type=Issue.IssueType.BUG,
        )

    def test_issue_list_requires_login(self):
        response = self.client.get(reverse("issue_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_logged_in_user_can_view_issue_list(self):
        self.client.force_login(self.reporter)

        response = self.client.get(reverse("issue_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login page bug")

    def test_any_logged_in_user_can_view_issue_details(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("issue_detail", args=[self.issue.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login page bug")

    def test_search_finds_issue_by_title(self):
        self.client.force_login(self.reporter)

        response = self.client.get(
            reverse("issue_list"),
            {"search": "Login page bug"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login page bug")

    def test_status_filter_returns_matching_issues(self):
        self.client.force_login(self.reporter)

        response = self.client.get(
            reverse("issue_list"),
            {"status": Issue.Status.OPEN},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login page bug")

    def test_project_member_can_create_issue(self):
        self.client.force_login(self.reporter)

        response = self.client.post(
            reverse("issue_create"),
            {
                "title": "Dashboard layout bug",
                "description": "Layout breaks on smaller screens",
                "project": self.project.pk,
                "assignee": "",
                "status": Issue.Status.OPEN,
                "priority": Issue.Priority.MEDIUM,
                "issue_type": Issue.IssueType.BUG,
            },
        )

        self.assertEqual(response.status_code, 302)

        created_issue = Issue.objects.get(
            title="Dashboard layout bug"
        )
        self.assertEqual(created_issue.reporter, self.reporter)

        self.assertTrue(
            IssueActivity.objects.filter(
                issue=created_issue,
                action=IssueActivity.Action.CREATED,
            ).exists()
        )

    def test_nonmember_cannot_create_issue_in_restricted_project(self):
        restricted_project = Project.objects.create(
            name="Restricted Project",
            description="Only the owner can create issues here",
            owner=self.owner,
        )
        self.client.force_login(self.reporter)

        response = self.client.post(
            reverse("issue_create"),
            {
                "title": "Unauthorized issue",
                "description": "This should not be saved",
                "project": restricted_project.pk,
                "assignee": "",
                "status": Issue.Status.OPEN,
                "priority": Issue.Priority.MEDIUM,
                "issue_type": Issue.IssueType.BUG,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Issue.objects.filter(title="Unauthorized issue").exists()
        )

    def test_any_logged_in_user_can_add_comment(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("issue_detail", args=[self.issue.pk]),
            {"body": "I can reproduce this bug."},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            IssueComment.objects.filter(
                issue=self.issue,
                author=self.other_user,
                body="I can reproduce this bug.",
            ).exists()
        )
        self.assertTrue(
            IssueActivity.objects.filter(
                issue=self.issue,
                action=IssueActivity.Action.COMMENTED,
            ).exists()
        )

    def test_reporter_can_open_issue_edit_page(self):
        self.client.force_login(self.reporter)

        response = self.client.get(
            reverse("issue_update", args=[self.issue.pk])
        )

        self.assertEqual(response.status_code, 200)

    def test_unrelated_user_cannot_edit_issue(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("issue_update", args=[self.issue.pk])
        )

        self.assertEqual(response.status_code, 403)

    def test_unrelated_user_cannot_delete_issue(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("issue_delete", args=[self.issue.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Issue.objects.filter(pk=self.issue.pk).exists()
        )

    def test_project_owner_can_edit_issue(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse("issue_update", args=[self.issue.pk])
        )

        self.assertEqual(response.status_code, 200)
