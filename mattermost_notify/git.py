# Copyright (C) 2022 Jaspar Stach <jasp.stac@gmx.de>

# pylint: disable=invalid-name

import json
import os
from argparse import ArgumentParser, Namespace
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import httpx
from pontos.terminal.terminal import ConsoleTerminal


class Status(Enum):
    SUCCESS = ":white_check_mark: success"
    FAILURE = ":x: failure"
    UNKNOWN = ":grey_question: unknown"
    CANCELLED = ":no_entry_sign: canceled"

    def __str__(self):
        return self.name


LONG_TEMPLATE = (
    "#### Status: {status}\n\n"
    "| Workflow | {workflow} |\n"
    "| --- | --- |\n"
    "| Repository (branch) | {repository} ({branch}) |\n"
    "| Related commit | {commit} |\n\n"
    "{highlight}"
)

SHORT_TEMPLATE = "{status}: {workflow} ({commit})  in {repository} ({branch})"

DEFAULT_GIT = "https://github.com"


def linker(name: str, url: Optional[str] = None) -> str:
    # create a markdown link
    return f"[{name}]({url})" if url else name


def get_github_event_json(term: ConsoleTerminal) -> dict[str, Any]:
    github_event_path = os.environ.get("GITHUB_EVENT_PATH")

    if not github_event_path:
        return {}

    json_path = Path(github_event_path)

    try:
        with json_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        term.error("Could not find GitHub Event JSON file.")
    except json.JSONDecodeError:
        term.error("Could not decode the JSON object.")

    return {}


def fill_template(
    *,
    short: bool = False,
    highlight: Optional[list[str]] = None,
    commit: Optional[str] = None,
    branch: Optional[str] = None,
    repository: Optional[str] = None,
    status: Optional[str] = None,
    workflow_id: Optional[str] = None,
    workflow_name: Optional[str] = None,
    terminal: ConsoleTerminal,
) -> str:
    template = LONG_TEMPLATE
    if short:
        template = SHORT_TEMPLATE

    # try to get information from the GiTHUB_EVENT json
    event = get_github_event_json(terminal)
    workflow_info: dict[str, Any] = event.get("workflow_run", {})

    status = status if status else workflow_info.get("conclusion")
    workflow_status = Status[status.upper()] if status else Status.UNKNOWN

    workflow_name: str = (
        workflow_name if workflow_name else workflow_info.get("name", "")
    )

    head_repo: dict[str, Any] = workflow_info.get("head_repository", {})
    repository = repository if repository else head_repo.get("full_name", "")
    repository_url = (
        f"{DEFAULT_GIT}/{repository}"
        if repository
        else head_repo.get("html_url", "")
    )

    branch: str = branch if branch else workflow_info.get("head_branch", "")
    branch_url = f"{repository_url}/tree/{branch}"

    workflow_url = (
        f"{repository}/actions/runs/{workflow_id}"
        if repository
        else workflow_info.get("html_url", "")
    )

    if commit:
        commit_url = f"{repository_url}/commit/{commit}"
        commit_message = commit
    else:
        head_commit = workflow_info.get("head_commit", {})
        commit_url = f'{repository_url}/commit/{head_commit.get("id", "")}'
        commit_message: str = head_commit["message"].split("\n", 1)[0]

    highlight_str = ""
    if highlight and status is not Status.SUCCESS:
        highlight_str = "".join([f"@{h}\n" for h in highlight])

    return template.format(
        status=workflow_status.value,
        workflow=linker(workflow_name, workflow_url),
        repository=linker(repository, repository_url),
        branch=linker(branch, branch_url),
        commit=linker(commit_message, commit_url),
        highlight=highlight_str,
    )


def parse_args(args=None) -> Namespace:
    parser = ArgumentParser(prog="mnotify-git")

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


def main() -> None:
    parsed_args: Namespace = parse_args()

    term = ConsoleTerminal()

    if not parsed_args.free:
        body = fill_template(args=parsed_args, term=term)

        data = {"channel": parsed_args.channel, "text": body}
    else:
        data = {"channel": parsed_args.channel, "text": parsed_args.free}

    response = httpx.post(url=parsed_args.url, json=data)
    if response.is_success:
        term.ok(
            f"Successfully posted on Mattermost channel {parsed_args.channel}"
        )
    else:
        term.error("Failed to post on Mattermost")


if __name__ == "__main__":
    main()
