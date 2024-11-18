# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from enum import Enum


class Status(Enum):
    SUCCESS = ":white_check_mark: success"
    FAILURE = ":x: failure"
    UNKNOWN = ":grey_question: unknown"
    CANCELLED = ":no_entry_sign: canceled"
    WARNING = ":warning: warning"

    def __str__(self):
        return self.name


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
