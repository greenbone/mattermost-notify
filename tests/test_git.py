# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa: E501

import unittest
from unittest.mock import MagicMock, patch

from mattermost_notify.git import fill_template, linker
from mattermost_notify.status import Status


class LinkerTestCase(unittest.TestCase):
    def test_linker(self):
        self.assertEqual(linker("foo", "www.foo.com"), "[foo](www.foo.com)")

    def test_no_url(self):
        self.assertEqual(linker("foo"), "foo")
        self.assertEqual(linker("foo", None), "foo")
        self.assertEqual(linker("foo", ""), "foo")


class FillTemplateTestCase(unittest.TestCase):
    def test_success_no_highlight(self):
        actual = fill_template(
            highlight=["user1", "user2"],
            status=Status.SUCCESS.name,
        )
        expected = """#### Status: :white_check_mark: success

| Workflow |  |
| --- | --- |
| Repository (branch) |  ([](/tree/)) |
| Related commit | [](/commit/) |

"""
        self.assertEqual(expected, actual)

    def test_warning_no_highlight(self):
        actual = fill_template(
            highlight=["user1", "user2"],
            status=Status.WARNING.name,
        )
        expected = """#### Status: :warning: warning

| Workflow |  |
| --- | --- |
| Repository (branch) |  ([](/tree/)) |
| Related commit | [](/commit/) |

"""
        self.assertEqual(expected, actual)

    def test_failure_highlight(self):
        actual = fill_template(
            highlight=["user1", "user2"],
            status=Status.FAILURE.name,
        )
        expected = """#### Status: :x: failure

| Workflow |  |
| --- | --- |
| Repository (branch) |  ([](/tree/)) |
| Related commit | [](/commit/) |

@user1
@user2
"""
        self.assertEqual(expected, actual)

    def test_short_template(self):
        actual = fill_template(
            short=True,
            status=Status.SUCCESS.name,
            workflow_name="SomeWorkflow",
            workflow_id="w1",
            commit="12345",
            commit_message="Add foo",
            repository="foo/bar",
            branch="main",
        )
        expected = (
            ":white_check_mark: success: [SomeWorkflow](https://github.com/foo/bar/actions/runs/w1) |"
            " [foo/bar](https://github.com/foo/bar) (b [main](https://github.com/foo/bar/tree/main)) "
        )
        self.assertEqual(expected, actual)

    def test_template(self):
        actual = fill_template(
            short=False,
            status=Status.SUCCESS.name,
            workflow_name="SomeWorkflow",
            workflow_id="w1",
            commit="12345",
            commit_message="Add foo",
            repository="foo/bar",
            branch="main",
        )
        expected = """#### Status: :white_check_mark: success

| Workflow | [SomeWorkflow](https://github.com/foo/bar/actions/runs/w1) |
| --- | --- |
| Repository (branch) | [foo/bar](https://github.com/foo/bar) ([main](https://github.com/foo/bar/tree/main)) |
| Related commit | [Add foo](https://github.com/foo/bar/commit/12345) |

"""
        self.assertEqual(expected, actual)

    @patch("mattermost_notify.git.get_github_event_json")
    def test_template_data_from_github_event(self, mock: MagicMock):
        event = {
            "workflow_run": {
                "conclusion": Status.SUCCESS.name,
                "name": "SomeWorkflow",
                "head_repository": {
                    "full_name": "foo/bar",
                    "html_url": "https://github.com/foo/bar",
                },
                "head_branch": "main",
                "head_commit": {"id": "12345", "message": "Add foo"},
                "workflow_id": "w1",
            }
        }
        mock.return_value = event

        actual = fill_template()
        expected = """#### Status: :white_check_mark: success

| Workflow | [SomeWorkflow](https://github.com/foo/bar/actions/runs/w1) |
| --- | --- |
| Repository (branch) | [foo/bar](https://github.com/foo/bar) ([main](https://github.com/foo/bar/tree/main)) |
| Related commit | [Add foo](https://github.com/foo/bar/commit/12345) |

"""
        self.assertEqual(expected, actual)

    # NEW:  Tests for deployment metadata templates
    def test_deployment_template(self):
        """Test deployment template with deployment metadata"""
        actual = fill_template(
            status=Status.SUCCESS.name,
            workflow_name="Stage Rebuild and Deploy",
            workflow_id="w1",
            commit="12345",
            commit_message="Update compose files",
            repository="foo/bar",
            branch="main",
            product="asset",
            stage="integration",
            version="1.15.1-alpha.10",
            notification_type="deployment",
        )
        self.assertIn("Deployment: success", actual)
        self.assertIn(
            "Product: asset | Stage: integration | Version: 1.15.1-alpha.10",
            actual,
        )
        self.assertIn(
            "[Update compose files](https://github.com/foo/bar/commit/12345)",
            actual,
        )
        self.assertIn(
            "[Stage Rebuild and Deploy](https://github.com/foo/bar/actions/runs/w1)",
            actual,
        )

    def test_service_update_template(self):
        """Test service update template with service metadata"""
        actual = fill_template(
            status=Status.SUCCESS.name,
            workflow_name="Build and Push Service",
            workflow_id="w2",
            commit="a1b2c3d",
            commit_message="Add new feature",
            repository="greenbone/asset-management-backend",
            branch="main",
            service="asset-management-backend",
            version="1.15.2",
            notification_type="service-update",
        )
        self.assertIn("Service Update:  success", actual)
        self.assertIn(
            "Service: asset-management-backend | Version: 1.15.2", actual
        )
        self.assertIn(
            "[Add new feature](https://github.com/greenbone/asset-management-backend/commit/a1b2c3d)",
            actual,
        )
        self.assertIn(
            "[Build and Push Service](https://github.com/greenbone/asset-management-backend/actions/runs/w2)",
            actual,
        )

    def test_stage_transition_template(self):
        """Test stage transition template with transition metadata"""
        actual = fill_template(
            status=Status.SUCCESS.name,
            workflow_name="Stage Transition",
            workflow_id="w3",
            commit="f4e5d6c",
            commit_message="Promote to staging",
            repository="greenbone/automatix",
            branch="main",
            product="lookout",
            from_stage="testing",
            to_stage="staging",
            version="1.1.7-alpha.5",
            notification_type="stage-transition",
        )
        self.assertIn("Stage Transition: success", actual)
        self.assertIn(
            "Product: lookout | testing → staging | Version: 1.1.7-alpha.5",
            actual,
        )
        self.assertIn(
            "[Promote to staging](https://github.com/greenbone/automatix/commit/f4e5d6c)",
            actual,
        )
        self.assertIn(
            "[Stage Transition](https://github.com/greenbone/automatix/actions/runs/w3)",
            actual,
        )

    def test_release_template(self):
        """Test release template with release metadata"""
        actual = fill_template(
            status=Status.SUCCESS.name,
            workflow_name="Release",
            workflow_id="w4",
            commit="k0l1m2n",
            commit_message="Release v0.15.0",
            repository="greenbone/management-console",
            branch="main",
            product="management-console",
            version="0.15.0",
            notification_type="release",
        )
        self.assertIn("Release: success", actual)
        self.assertIn("Product: management-console | Version: 0.15.0", actual)
        self.assertIn(
            "[Release v0.15.0](https://github.com/greenbone/management-console/commit/k0l1m2n)",
            actual,
        )
        self.assertIn(
            "[Release](https://github.com/greenbone/management-console/actions/runs/w4)",
            actual,
        )

    def test_hotfix_template(self):
        """Test hotfix template with hotfix metadata"""
        actual = fill_template(
            status=Status.SUCCESS.name,
            workflow_name="Hotfix Release",
            workflow_id="w5",
            commit="p9q8r7s",
            commit_message="Hotfix: Critical security patch",
            repository="greenbone/security-intelligence",
            branch="main",
            product="security-intelligence",
            version="1.2.1",
            notification_type="hotfix",
        )
        self.assertIn("Hotfix:  success", actual)
        self.assertIn("Product: security-intelligence | Version: 1.2.1", actual)
        self.assertIn(
            "[Hotfix: Critical security patch](https://github.com/greenbone/security-intelligence/commit/p9q8r7s)",
            actual,
        )
        self.assertIn(
            "[Hotfix Release](https://github.com/greenbone/security-intelligence/actions/runs/w5)",
            actual,
        )

    def test_deployment_template_with_failure(self):
        """Test deployment template when deployment fails"""
        actual = fill_template(
            status=Status.FAILURE.name,
            workflow_name="Stage Deploy",
            workflow_id="w6",
            commit="t0u1v2w",
            commit_message="Add feature X",
            repository="greenbone/automatix",
            branch="main",
            product="asset",
            stage="testing",
            version="1.15.1-alpha.11",
            notification_type="deployment",
            highlight=["devops"],
        )
        self.assertIn("Deployment: failure", actual)
        self.assertIn(
            "Product: asset | Stage: testing | Version: 1.15.1-alpha.11", actual
        )
        self.assertIn("@devops", actual)

    def test_backward_compatibility_no_metadata(self):
        """Test that function still works with no deployment metadata (legacy mode)"""
        actual = fill_template(
            short=False,
            status=Status.SUCCESS.name,
            workflow_name="Legacy Workflow",
            workflow_id="w7",
            commit="abc123",
            commit_message="Legacy commit",
            repository="foo/bar",
            branch="main",
        )
        # Should use LONG_TEMPLATE when no metadata provided
        self.assertIn("#### Status:", actual)
        self.assertIn("| Workflow |", actual)
