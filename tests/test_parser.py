# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mattermost_notify.parser import parse_args


class ParseArgsTestCase(unittest.TestCase):
    def test_defaults(self):
        parsed_args = parse_args(["www.url.de", "channel"])

        self.assertEqual(parsed_args.url, "www.url.de")
        self.assertEqual(parsed_args.channel, "channel")

        self.assertFalse(parsed_args.short)
        self.assertEqual(parsed_args.status, "SUCCESS")
        self.assertIsNone(parsed_args.repository)
        self.assertIsNone(parsed_args.branch)
        self.assertIsNone(parsed_args.workflow)
        self.assertIsNone(parsed_args.workflow_name)
        self.assertIsNone(parsed_args.commit)
        self.assertIsNone(parsed_args.free)
        self.assertIsNone(parsed_args.highlight)

    def test_fail_argument_parsing(self):
        with self.assertRaises(SystemExit):
            parse_args(["-s"])

    def test_parse_status(self):
        parsed_args = parse_args(
            [
                "www.url.de",
                "channel",
                "-S",
                "failure",
            ]
        )
        self.assertEqual(parsed_args.status, "failure")

    def test_parse_short(self):
        parsed_args = parse_args(
            [
                "www.url.de",
                "channel",
                "--short",
            ]
        )
        self.assertTrue(parsed_args.short)

        parsed_args = parse_args(
            [
                "www.url.de",
                "channel",
                "-s",
            ]
        )
        self.assertTrue(parsed_args.short)

    def test_parse_repository(self):
        parsed_args = parse_args(["www.url.de", "channel", "-r", "foo/bar"])
        self.assertEqual(parsed_args.repository, "foo/bar")

        parsed_args = parse_args(
            ["www.url.de", "channel", "--repository", "foo/bar"]
        )
        self.assertEqual(parsed_args.repository, "foo/bar")

    def test_parse_branch(self):
        parsed_args = parse_args(["www.url.de", "channel", "-b", "foo"])
        self.assertEqual(parsed_args.branch, "foo")

        parsed_args = parse_args(["www.url.de", "channel", "--branch", "foo"])
        self.assertEqual(parsed_args.branch, "foo")

    def test_parse_workflow(self):
        parsed_args = parse_args(["www.url.de", "channel", "-w", "w1"])
        self.assertEqual(parsed_args.workflow, "w1")

        parsed_args = parse_args(["www.url.de", "channel", "--workflow", "w1"])
        self.assertEqual(parsed_args.workflow, "w1")

    def test_parse_workflow_name(self):
        parsed_args = parse_args(["www.url.de", "channel", "-n", "foo"])
        self.assertEqual(parsed_args.workflow_name, "foo")

        parsed_args = parse_args(
            ["www.url.de", "channel", "--workflow_name", "foo"]
        )
        self.assertEqual(parsed_args.workflow_name, "foo")

    def test_parse_commit(self):
        parsed_args = parse_args(["www.url.de", "channel", "--commit", "1234"])
        self.assertEqual(parsed_args.commit, "1234")

    def test_parse_commit_message(self):
        parsed_args = parse_args(
            ["www.url.de", "channel", "--commit-message", "foo bar"]
        )
        self.assertEqual(parsed_args.commit_message, "foo bar")

    def test_parse_free(self):
        parsed_args = parse_args(
            ["www.url.de", "channel", "--free", "lorem ipsum"]
        )
        self.assertEqual(parsed_args.free, "lorem ipsum")

    def test_parse_highlight(self):
        parsed_args = parse_args(
            [
                "www.url.de",
                "channel",
                "--highlight",
                "user1",
                "user2",
            ]
        )
        self.assertEqual(parsed_args.highlight, ["user1", "user2"])
