# Copyright (C) 2022 Jaspar Stach <jasp.stac@gmx.de>

from argparse import ArgumentParser, Namespace
from enum import Enum

import requests

class Status(Enum):
    success = ':white_check_mark: success'
    failure = ':x: failure'

    def __str__(self):
        return self.name


LONG_TEMPLATE = (
    '#### Status: {status}\n\n'
    '| Workflow | {workflow} |\n'
    '| --- | --- |\n'
    '| Repository | {repository} |\n'
    '| Branch | {branch} |\n'
)

SHORT_TEMPLATE = (
    '{status}: {workflow} in {repository} ({branch})'
)

DEFAULT_GIT = 'https://github.com'

def _linker(name:str, url:str) -> str:
    # create a markdown link
    return f'[{name}]({url})'

def parse_args(args=None) -> Namespace:
    parser = ArgumentParser(prog='mnotify-git')

    parser.add_argument(
        '-u',
        '--url',
        help="Mattermost (WEBHOOK) URL",
        type=str,
        required=True,
    )

    parser.add_argument(
        '-c',
        '--channel',
        type=str,
        help="Mattermost Channel",
        required=True,
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
        default=Status.success.name,
        help="Status of Job",
    )

    parser.add_argument(
        '-r',
        '--repository',
        type=str,
        help='git repository name (orga/repo)'
    )

    parser.add_argument(
        '-b',
        '--branch',
        type=str,
        help='git branch'
    )

    parser.add_argument(
        '-w',
        '--workflow',
        type=str,
        help='hash/ID of the workflow'
    )

    parser.add_argument(
        '--free',
        type=str,
    )

    return parser.parse_args(args=args)

def main():
    parsed_args: Namespace = parse_args()

    if not parsed_args.free:
        template = LONG_TEMPLATE
        if parsed_args.short:
            template = SHORT_TEMPLATE

        git_url = f'{DEFAULT_GIT}/{parsed_args.repository}'
        workflow_url = f'{git_url}/actions/runs/{parsed_args.workflow}'

        body = template.format(
            status = Status[parsed_args.status].value,
            workflow = _linker(parsed_args.workflow, workflow_url),
            repository = _linker(parsed_args.repository, git_url),
            branch = parsed_args.branch,
        )

        
        data = (
            f'{{"channel": "{parsed_args.channel}", '
            f'"text": "{body}"}}'
        )
    else:
        data = (
            f'{{"channel": "{parsed_args.channel}", '
            f'"text": "{parsed_args.free}"}}'
        )
        print(data)
    headers = {}
    response = requests.post(
        url=parsed_args.url,
        headers=headers,
        data=data
    )
    print(response)

if __name__ == '__main__':
    main()
