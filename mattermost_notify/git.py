# Copyright (C) 2022 Jaspar Stach <jasp.stac@gmx.de>

# pylint: disable=invalid-name

from argparse import ArgumentParser, Namespace
from enum import Enum
import json
import os
from pathlib import Path
from typing import Optional

from pontos.terminal.terminal import ConsoleTerminal

import requests


class Status(Enum):
    SUCCESS = ':white_check_mark: success'
    FAILURE = ':x: failure'

    def __str__(self):
        return self.name


LONG_TEMPLATE = (
    '#### Status: {status}\n\n'
    '| Workflow | {workflow} |\n'
    '| --- | --- |\n'
    '| Repository (branch) | {repository} ({branch}) |\n'
    '| Related commit | {commit} |\n'
)

SHORT_TEMPLATE = '{status}: {workflow} ({commit})  in {repository} ({branch})'

DEFAULT_GIT = 'https://github.com'


def _linker(name: str, url: str) -> str:
    # create a markdown link
    return f'[{name}]({url})'


def get_github_event_json(term: ConsoleTerminal) -> Optional[dict]:
    json_path = Path(os.environ.get('GITHUB_EVENT_PATH'))

    try:
        with open(json_path, 'r', encoding="utf-8") as f:
            event = json.load(f)
    except FileNotFoundError:
        term.error("Could not find GitHub Event JSON file.")
        event = None
    except json.JSONDecodeError:
        term.error("Could not decode the JSON object.")
        event = None
    return event


def fill_template(args: Namespace, term: ConsoleTerminal):
    template = LONG_TEMPLATE
    if args.short:
        template = SHORT_TEMPLATE

    event: dict = get_github_event_json(term)
    if not event:
        git_url = f'{DEFAULT_GIT}/{args.repository}'
        workflow_url = f'{git_url}/actions/runs/{args.workflow}'

        return template.format(
            status=Status[args.status.upper()].value,
            workflow=_linker(args.workflow_name, workflow_url),
            repository=_linker(args.repository, git_url),
            branch=args.branch,
        )

    workflow_info = event["workflow_run"]
    workflow_link = _linker(workflow_info["name"], workflow_info['html_url'])
    head_commit = workflow_info["head_commit"]
    head_repo = workflow_info["head_repository"]
    repo_url = head_repo["html_url"]
    branch = _linker(
        workflow_info["head_branch"],
        f'{repo_url}/tree/{workflow_info["head_branch"]}',
    )
    commit_name: str = head_commit["message"].split('\n', 1)[0]
    commit = _linker(commit_name, f'{repo_url}/commit/{head_commit["id"]}')
    status = Status[workflow_info['conclusion'].upper()].value

    return template.format(
        status=status,
        workflow=workflow_link,
        repository=_linker(head_repo["full_name"], repo_url),
        branch=branch,
        commit=commit,
    )


def parse_args(args=None) -> Namespace:
    parser = ArgumentParser(prog='mnotify-git')

    parser.add_argument(
        'url',
        help="Mattermost (WEBHOOK) URL",
        type=str,
    )

    parser.add_argument(
        'channel',
        type=str,
        help="Mattermost Channel",
    )

    parser.add_argument(
        '-s',
        '--short',
        action='store_true',
        help='Send a short single line message',
    )

    parser.add_argument(
        '-S',
        '--status',
        type=str,
        choices=['success', 'failure'],
        default=Status.SUCCESS.name,
        help="Status of Job",
    )

    parser.add_argument(
        '-r', '--repository', type=str, help='git repository name (orga/repo)'
    )

    parser.add_argument('-b', '--branch', type=str, help='git branch')

    parser.add_argument(
        '-w', '--workflow', type=str, help='hash/ID of the workflow'
    )

    parser.add_argument(
        '-n', '--workflow_name', type=str, help='name of the workflow'
    )

    parser.add_argument(
        '--free',
        type=str,
        help="Print a free-text message to the given channel",
    )

    return parser.parse_args(args=args)


def main():
    parsed_args: Namespace = parse_args()

    term = ConsoleTerminal()

    if not parsed_args.free:
        body = fill_template(args=parsed_args, term=term)

        data = f'{{"channel": "{parsed_args.channel}", ' f'"text": "{body}"}}'
    else:
        data = (
            f'{{"channel": "{parsed_args.channel}", '
            f'"text": "{parsed_args.free}"}}'
        )
    headers = {}
    response = requests.post(url=parsed_args.url, headers=headers, data=data)
    status = response.status_code
    if status == 200:
        term.ok(
            f"Successfully posted on Mattermost channel {parsed_args.channel}"
        )
    else:
        term.error("Failed to post on Mattermost")


if __name__ == '__main__':
    main()
