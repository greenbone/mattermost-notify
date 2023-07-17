# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from enum import Enum


class Status(Enum):
    SUCCESS = ":white_check_mark: success"
    FAILURE = ":x: failure"
    UNKNOWN = ":grey_question: unknown"
    CANCELLED = ":no_entry_sign: canceled"

    def __str__(self):
        return self.name
