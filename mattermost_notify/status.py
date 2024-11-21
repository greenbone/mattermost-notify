# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from enum import Enum


class Status(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    UNKNOWN = "unknown"
    CANCELLED = "canceled"
    WARNING = "warning"

    def __str__(self):
        return self.name

def string_to_status(status_str: str) -> Status:
    return Status(status_str.upper()) if status_str else Status.UNKNOWN


def status_to_emoji(status: Status) -> str:
    if status == Status.SUCCESS:
        return ":white_check_mark:"
    elif status == Status.FAILURE:
        return ":x:"
    elif status == Status.CANCELLED:
        return ":no_entry_sign:"
    elif status == Status.WARNING:
        return ":warning:"
    else:
        return ":grey_question:"
