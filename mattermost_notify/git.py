# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# pylint: disable=invalid-name

import json
import os
from pathlib import Path
from typing import Any, Optional

from pontos.git import Git
from pontos.terminal import RichTerminal

from mattermost_notify.errors import MattermostNotifyError
from mattermost_notify.parser import parse_args
from mattermost_notify.post import post
from mattermost_notify.status import Status

LONG_TEMPLATE = (
    "#### Status: {status}\n\n"
    "| Workflow | {workflow} |\n"
    "| --- | --- |\n"
    "| Repository (branch) | {repository} ({branch}) |\n"
    "| Related commit | {commit} |\n\n"
    "{highlight}"
)

SHORT_TEMPLATE = "{status}: {workflow} ({commit}) in {repository} ({branch})"

DEFAULT_GIT = "https://github.com"


def linker(name: str, url: Optional[str] = None) -> str:
    # create a markdown link
    return f"[{name}]({url})" if url else name


def get_github_event_json() -> dict[str, Any]:
    github_event_path = os.environ.get("GITHUB_EVENT_PATH")

    if not github_event_path:
        return {}

    json_path = Path(github_event_path)

    try:
        with json_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise MattermostNotifyError("Could not find GitHub Event JSON file.")
    except json.JSONDecodeError:
        raise MattermostNotifyError("Could not decode the JSON object.")


def fill_template(
    *,
    short: bool = False,
    highlight: Optional[list[str]] = None,
    commit: Optional[str] = None,
    commit_message: Optional[str] = None,
    branch: Optional[str] = None,
    repository: Optional[str] = None,
    status: Optional[str] = None,
    workflow_id: Optional[str] = None,
    workflow_name: Optional[str] = None,
) -> str:
    template = SHORT_TEMPLATE if short else LONG_TEMPLATE

    # try to get information from the GiTHUB_EVENT json
    event = get_github_event_json()
    workflow_info: dict[str, Any] = event.get("workflow_run", {})

    status = status if status else workflow_info.get("conclusion")
    workflow_status = Status[status.upper()] if status else Status.UNKNOWN

    used_workflow_name: str = (
        workflow_name if workflow_name else workflow_info.get("name", "")
    )
    used_workflow_id = (
        workflow_id if workflow_id else workflow_info.get("workflow_id", "")
    )

    head_repo: dict[str, Any] = workflow_info.get("head_repository", {})
    repository = repository if repository else head_repo.get("full_name", "")
    repository_url = (
        f"{DEFAULT_GIT}/{repository}"
        if repository
        else head_repo.get("html_url", "")
    )

    used_branch: str = (
        branch if branch else workflow_info.get("head_branch", "")
    )
    branch_url = f"{repository_url}/tree/{used_branch}"

    workflow_url = (
        f"{repository_url}/actions/runs/{used_workflow_id}"
        if repository
        else workflow_info.get("html_url", "")
    )

    head_commit = workflow_info.get("head_commit", {})

    if commit:
        commit_url = f"{repository_url}/commit/{commit}"

        if not commit_message:
            commit_message = Git().show(
                format="format:%s", patch=False, objects=commit  # type: ignore[assignment] # noqa: E501
            )
    else:
        commit_url = f'{repository_url}/commit/{head_commit.get("id", "")}'

        if not commit_message:
            commit_message = head_commit.get("message", "").split("\n", 1)[0]

    highlight_str = ""
    if highlight and workflow_status is not Status.SUCCESS:
        highlight_str = "".join([f"@{h}\n" for h in highlight])

    return template.format(
        status=workflow_status.value,
        workflow=linker(used_workflow_name, workflow_url),
        repository=linker(repository, repository_url),
        branch=linker(used_branch, branch_url),
        commit=linker(commit_message, commit_url),  # type: ignore[arg-type]
        highlight=highlight_str,
    )


def main() -> None:
    parsed_args = parse_args()

    term = RichTerminal()

    try:
        if not parsed_args.free:
            body = fill_template(
                highlight=parsed_args.highlight,
                short=parsed_args.short,
                branch=parsed_args.branch,
                commit=parsed_args.commit,
                repository=parsed_args.repository,
                status=parsed_args.status,
                workflow_id=parsed_args.workflow,
                workflow_name=parsed_args.workflow_name,
            )
            post(parsed_args.url, parsed_args.channel, body)
        else:
            post(parsed_args.url, parsed_args.channel, parsed_args.free)

        term.ok(
            "Successfully posted on Mattermost channel "
            f"{parsed_args.channel}"
        )
    except MattermostNotifyError as e:
        term.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
