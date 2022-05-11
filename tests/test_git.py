# Copyright (C) 2022 Jaspar Stach <jasp.stac@gmx.de>

import unittest

from mattermost_notify.git import _linker as linker, parse_args


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
