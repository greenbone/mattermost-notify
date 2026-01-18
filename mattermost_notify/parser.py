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
        choices=["success", "failure", "warning"],
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

    parser.add_argument(
        "--product",
        type=str,
        help="Product name (asset, lookout, detect, management-console, security-intelligence, etc.)",
    )

    parser.add_argument(
        "--stage",
        type=str,
        help="Deployment stage (dev, integration, testing, staging, production)",
    )

    parser.add_argument(
        "--version",
        type=str,
        help="Product/Release version (e.g., 1.15.1, 1.15.1-alpha. 5)",
    )

    parser.add_argument(
        "--service",
        type=str,
        help="Service name if single service was updated",
    )

    parser.add_argument(
        "--from-stage",
        type=str,
        help="Source stage in transition (e.g., testing)",
    )

    parser.add_argument(
        "--to-stage",
        type=str,
        help="Target stage in transition (e.g., staging)",
    )

    parser.add_argument(
        "--notification-type",
        type=str,
        choices=[
            "deployment",
            "service-update",
            "stage-transition",
            "release",
            "hotfix",
        ],
        default="deployment",
        help="Type of notification",
    )

    parser.add_argument(
        "--changed-services",
        type=str,
        help="Comma-separated list of changed services",
    )

    return parser.parse_args(args=args)
