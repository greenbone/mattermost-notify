# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser, Namespace

from mattermost_notify.status import Status


def parse_args(args=None) -> Namespace:
    parser = ArgumentParser()

    parser.add_argument(
        "url",
        help="Mattermost (WEBHOOK) URL",
        type=str,
    )

    parser.add_argument(
        "channel",
        type=str,
        help="Mattermost Channel",
    )

    parser.add_argument(
        "-s",
        "--short",
        action="store_true",
        help="Send a short single line message",
    )

    parser.add_argument(
        "-S",
        "--status",
        type=str,
        choices=["success", "failure"],
        default=Status.SUCCESS.name,
        help="Status of Job",
    )

    parser.add_argument(
        "-r", "--repository", type=str, help="git repository name (orga/repo)"
    )

    parser.add_argument("-b", "--branch", type=str, help="git branch")

    parser.add_argument(
        "-w", "--workflow", type=str, help="hash/ID of the workflow"
    )

    parser.add_argument(
        "-n", "--workflow_name", type=str, help="name of the workflow"
    )

    parser.add_argument("--commit", help="Commit ID to use")
    parser.add_argument("--commit-message", help="Commit Message to use")

    parser.add_argument(
        "--free",
        type=str,
        help="Print a free-text message to the given channel",
    )

    parser.add_argument(
        "--highlight",
        nargs="+",
        help="List of persons to highlight in the channel",
    )

    return parser.parse_args(args=args)
