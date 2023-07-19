# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import MagicMock, patch

from mattermost_notify.errors import MattermostNotifyError
from mattermost_notify.post import post


class PostTestCase(unittest.TestCase):
    @patch("mattermost_notify.post.httpx.post", autospec=True)
    def test_success(self, post_mock: MagicMock):
        response = post_mock.return_value
        response.is_success = True

        post("https://some.mattermost.url", "FooChannel", "Some Message")

        post_mock.assert_called_once_with(
            url="https://some.mattermost.url",
            json={"channel": "FooChannel", "text": "Some Message"},
        )

    @patch("mattermost_notify.post.httpx.post", autospec=True)
    def test_failure(self, post_mock: MagicMock):
        response = post_mock.return_value
        response.is_success = False
        response.status_code = 500

        with self.assertRaisesRegex(
            MattermostNotifyError,
            "Failed to post on Mattermost. HTTP status was 500",
        ):
            post("https://some.mattermost.url", "FooChannel", "Some Message")

        post_mock.assert_called_once_with(
            url="https://some.mattermost.url",
            json={"channel": "FooChannel", "text": "Some Message"},
        )
