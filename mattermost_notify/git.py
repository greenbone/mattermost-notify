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
from mattermost_notify.status import Status, status_to_emoji

LONG_TEMPLATE = (
    "#### Status: {status_emoji} {status_text}\n\n"
    "| Workflow | {workflow} |\n"
    "| --- | --- |\n"
    "| Repository (branch) | {repository} ({branch}) |\n"
    "| Related commit | {commit} |\n\n"
    "{highlight}"
)

SHORT_TEMPLATE = (
    "{status_emoji} {status_text}: {workflow} | {repository} "
    "(b {branch}) {highlight}"
)

DEPLOYMENT_TEMPLATE = (
    "{status_emoji} **Deployment:** {status_text}{deployment_header}\n\n"
    "Workflow: {workflow}\n"
    "Branch: {branch}\n"
    "{highlight}"
)

SERVICE_UPDATE_TEMPLATE = (
    "{status_emoji} **Service Update:**  {status_text}{service_header}\n\n"
    "Workflow: {workflow}\n"
    "Branch: {branch}\n"
    "{highlight}"
)

STAGE_TRANSITION_TEMPLATE = (
    "{status_emoji} **Stage Transition:** {status_text}{transition_header}\n\n"
    "Workflow: {workflow}\n"
    "Branch: {branch}\n"
    "{highlight}"
)

RELEASE_TEMPLATE = (
    "{status_emoji} **Release:** {status_text}{release_header}\n\n"
    "Workflow: {workflow}\n"
    "Branch: {branch}\n"
    "{highlight}"
)

HOTFIX_TEMPLATE = (
    "{status_emoji} **Hotfix:** {status_text}{hotfix_header}\n\n"
    "Workflow: {workflow}\n"
    "Branch: {branch}\n"
    "{highlight}"
)

DEFAULT_GIT = "https://github.com"


def linker(name: Optional[str], url: Optional[str] = None) -> str:
    """create a markdown link"""
    if not name:
        return ""
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


def format_deployment_header(
    product: Optional[str], stage: Optional[str]
) -> str:
    """Build header for deployment notification, only showing non-empty fields"""
    parts = []
    if product:
        parts.append(f"**Product:** {product}")
    if stage:
        parts.append(f"**Stage:** {stage}")

    if parts:
        return " | " + " | ".join(parts)
    return ""


def format_service_header(
    service: Optional[str], version: Optional[str]
) -> str:
    """Build header for service update notification, only showing non-empty fields"""
    parts = []
    if service:
        parts.append(f"**Service:** {service}")
    if version:
        parts.append(f"**Version:** {version}")

    if parts:
        return " | " + " | ".join(parts)
    return ""


def format_transition_header(
    product: Optional[str], from_stage: Optional[str], to_stage: Optional[str]
) -> str:
    """Build header for stage transition notification, only showing non-empty fields"""
    parts = []
    if product:
        parts.append(f"**Product:** {product}")

    if from_stage and to_stage:
        parts.append(f"**Transition:** {from_stage} to {to_stage}")
    elif from_stage:
        parts.append(f"**From Stage:** {from_stage}")
    elif to_stage:
        parts.append(f"**To Stage:** {to_stage}")

    if parts:
        return " | " + " | ".join(parts)
    return ""


def format_release_header(
    product: Optional[str], version: Optional[str]
) -> str:
    """Build header for release/hotfix notification, only showing non-empty fields"""
    parts = []
    if product:
        parts.append(f"**Product:** {product}")
    if version:
        parts.append(f"**Version:** {version}")

    if parts:
        return " | " + " | ".join(parts)
    return ""


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
    product: Optional[str] = None,
    stage: Optional[str] = None,
    version: Optional[str] = None,
    service: Optional[str] = None,
    from_stage: Optional[str] = None,
    to_stage: Optional[str] = None,
    notification_type: str = "deployment",
    changed_services: Optional[str] = None,
) -> str:
    """
    Fill notification template with workflow metadata and optional deployment context.

    Automatically selects appropriate template based on notification_type and
    available deployment metadata (product, stage, version, service, etc.).

    Falls back to legacy LONG_TEMPLATE or SHORT_TEMPLATE if no deployment
    metadata is provided (fully backward compatible).
    """

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
    if highlight and workflow_status not in (Status.SUCCESS, Status.WARNING):
        highlight_str = "".join([f"@{h}\n" for h in highlight])

    # Check if deployment metadata is provided
    has_metadata = any([product, stage, version, service, from_stage, to_stage])

    # Select template based on metadata and notification type
    if has_metadata:
        if notification_type == "service-update":
            template = SERVICE_UPDATE_TEMPLATE
            service_header = format_service_header(service, version)
        elif notification_type == "stage-transition":
            template = STAGE_TRANSITION_TEMPLATE
            transition_header = format_transition_header(
                product, from_stage, to_stage
            )
        elif notification_type == "release":
            template = RELEASE_TEMPLATE
            release_header = format_release_header(product, version)
        elif notification_type == "hotfix":
            template = HOTFIX_TEMPLATE
            hotfix_header = format_release_header(product, version)
        else:
            template = DEPLOYMENT_TEMPLATE
            deployment_header = format_deployment_header(product, stage)
    else:
        # Fall back to legacy templates
        template = SHORT_TEMPLATE if short else LONG_TEMPLATE

    template_vars = {
        "status": workflow_status.value,
        "status_emoji": status_to_emoji(workflow_status),
        "status_text": str(workflow_status).lower(),
        "workflow": linker(used_workflow_name, workflow_url),
        "repository": linker(repository, repository_url),
        "branch": linker(used_branch, branch_url),
        "commit": linker(commit_message, commit_url),
        "highlight": highlight_str,
    }

    if has_metadata:
        if notification_type == "service-update":
            template_vars["service_header"] = service_header
        elif notification_type == "stage-transition":
            template_vars["transition_header"] = transition_header
        elif notification_type == "release":
            template_vars["release_header"] = release_header
        elif notification_type == "hotfix":
            template_vars["hotfix_header"] = hotfix_header
        else:
            template_vars["deployment_header"] = deployment_header

    return template.format(**template_vars)


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
                product=parsed_args.product,
                stage=parsed_args.stage,
                version=parsed_args.version,
                service=parsed_args.service,
                from_stage=parsed_args.from_stage,
                to_stage=parsed_args.to_stage,
                notification_type=parsed_args.notification_type,
                changed_services=parsed_args.changed_services,
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
