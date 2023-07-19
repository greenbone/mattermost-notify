# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import httpx
from pontos.typing import SupportsStr

from mattermost_notify.errors import MattermostNotifyError


def post(url: str, channel: str, text: SupportsStr) -> None:
    response = httpx.post(url=url, json={"channel": channel, "text": text})
    if not response.is_success:
        raise MattermostNotifyError(
            "Failed to post on Mattermost. HTTP status was "
            f"{response.status_code}"
        )
