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
            ":white_check_mark: success: [SomeWorkflow](https://github.com/foo/bar/actions/runs/w1) "
            "([Add foo](https://github.com/foo/bar/commit/12345)) in "
            "[foo/bar](https://github.com/foo/bar) ([main](https://github.com/foo/bar/tree/main))"
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
