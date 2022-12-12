# Copyright (C) 2022 Jaspar Stach <jasp.stac@gmx.de>

import unittest
from unittest.mock import MagicMock, patch

from mattermost_notify.git import _linker as linker
from mattermost_notify.git import fill_template, parse_args


class GitNotifyTestCase(unittest.TestCase):
    def test_linker(self):
        expected = "[foo](www.foo.com)"
        link = linker("foo", "www.foo.com")

        self.assertEqual(link, expected)

    def test_argument_parsing(self):
        parsed_args = parse_args(["www.url.de", "channel"])

        self.assertEqual(parsed_args.url, "www.url.de")
        self.assertEqual(parsed_args.channel, "channel")

    def test_fail_argument_parsing(self):
        with self.assertRaises(SystemExit):
            parse_args(["-s"])

    @patch("mattermost_notify.git.get_github_event_json")
    def test_no_highlight(self, event_mock: None):
        event_mock.return_value = None
        parsed_args = parse_args(
            ["www.url.de", "channel", "--highlight", "user1", "user2"]
        )
        rf = fill_template(parsed_args, MagicMock())
        rt = (
            "#### Status: :white_check_mark: success\n\n"
            "| Workflow | [None](https://githu"
            "b.com/None/actions/runs/None) |\n| --- | --- |"
            "\n| Repository (branch) | [None](https://githu"
            "b.com/None) (None) |\n| Related commit | not a"
            "vailable |\n\n"
        )
        print(rf)
        self.assertEqual(rf, rt)

    @patch("mattermost_notify.git.get_github_event_json")
    def test_highlight(self, event_mock: None):
        event_mock.return_value = None
        parsed_args = parse_args(
            [
                "www.url.de",
                "channel",
                "--highlight",
                "user1",
                "user2",
                "-S",
                "failure",
            ]
        )
        rf = fill_template(parsed_args, MagicMock())
        rt = (
            "#### Status: :x: failure\n\n"
            "| Workflow | [None](https://githu"
            "b.com/None/actions/runs/None) |\n| --- | --- |"
            "\n| Repository (branch) | [None](https://githu"
            "b.com/None) (None) |\n| Related commit | not a"
            "vailable |\n\n@user1\n@user2\n"
        )
        self.assertEqual(rf, rt)
