# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import httpx
from pontos.typing import SupportsStr

from mattermost_notify.errors import MattermostNotifyError


class Colors:
    """
    Colors namespace for mattermost notifications.
    The colors are borrowed from bootstrap 5.
    """

    SECONDARY = "#6c757d"
    SUCCESS = "#28a745"
    WARNING = "#e0a800"
    DANGER = "#c82333"


def post(
    url: str, channel: str, text: SupportsStr, color: str = Colors.SECONDARY
) -> None:
    """
    Post a message to a Mattermost channel.

    Args:
        url (str): The Mattermost webhook URL.
        channel (str): The channel name to post the message to.
        text (SupportsStr): The message content, markdown formatted.
        color (str, optional): The color of the message, visible as a
                               border on the left. Defaults to Colors.SECONDARY.

    Raises:
        MattermostNotifyError: If the HTTP request fails.
    """

    response = httpx.post(
        url=url,
        json={
            "channel": channel,
            "attachments": [
                {
                    "color": color,
                    "text": text,
                    "fallback": text,
                }
            ],
        },
    )

    if not response.is_success:
        raise MattermostNotifyError(
            "Failed to post on Mattermost. HTTP status was "
            f"{response.status_code}"
        )
