![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)

# mattermost-notify <!-- omit in toc -->

[![GitHub releases](https://img.shields.io/github/release/greenbone/mattermost-notify.svg)](https://github.com/greenbone/mattermost-notify/releases)
[![PyPI release](https://img.shields.io/pypi/v/mattermost-notify.svg)](https://pypi.org/project/mattermost-notify/)
[![code test coverage](https://codecov.io/gh/greenbone/mattermost-notify/branch/main/graph/badge.svg)](https://codecov.io/gh/greenbone/mattermost-notify)
[![Build and test](https://github.com/greenbone/mattermost-notify/actions/workflows/ci-python.yml/badge.svg)](https://github.com/greenbone/mattermost-notify/actions/workflows/ci-python.yml)

This tool is desired to post messages to a mattermost channel.
You will need a mattermost webhook URL and give a channel name.

## Table of Contents <!-- omit in toc -->

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Install using pip](#install-using-pip)
- [Usage](#usage)
  - [Notification templates](#notification-templates)
- [License](#license)

## Installation

### Requirements

Python 3.7 and later is supported.

### Install using pip

pip 19.0 or later is required.

You can install the latest stable release of **mattermost-notify** from the Python
Package Index (pypi) using [pip]

    python3 -m pip install --user mattermost-notify

## Usage

Print a free text message:
```
mnotify-git <hook_url> <channel> --free "What a pitty!"
```

Print a github workflow status (legacy long/short templates):
```
mnotify-git <hook_url> <channel> -S [success, failure, warning] -r <orga/repo> -b <branch> -w <workflow_id> -n <workflow_name>
```

### Notification templates

`--notification-type` is optional. Use it only when you want a specific template
(`deployment`, `service-update`, `stage-transition`, `release`, `hotfix`) and you
are passing deployment metadata.

Supported types:
- `deployment`
- `service-update`
- `stage-transition`
- `release`
- `hotfix`

#### Deployment
```
mnotify-git <hook_url> <channel> \
  --notification-type deployment \
  --product <product> \
  --stage <stage> \
  -S [success, failure, warning] \
  -r <orga/repo> -b <branch> -w <workflow_id> -n <workflow_name>
```

#### Service update
```
mnotify-git <hook_url> <channel> \
  --notification-type service-update \
  --service <service> \
  --version <version> \
  -S [success, failure, warning] \
  -r <orga/repo> -b <branch> -w <workflow_id> -n <workflow_name>
```

#### Stage transition
```
mnotify-git <hook_url> <channel> \
  --notification-type stage-transition \
  --product <product> \
  --from-stage <from_stage> \
  --to-stage <to_stage> \
  -S [success, failure, warning] \
  -r <orga/repo> -b <branch> -w <workflow_id> -n <workflow_name>
```

#### Release
```
mnotify-git <hook_url> <channel> \
  --notification-type release \
  --product <product> \
  --version <version> \
  -S [success, failure, warning] \
  -r <orga/repo> -b <branch> -w <workflow_id> -n <workflow_name>
```

#### Hotfix
```
mnotify-git <hook_url> <channel> \
  --notification-type hotfix \
  --product <product> \
  --version <version> \
  -S [success, failure, warning] \
  -r <orga/repo> -b <branch> -w <workflow_id> -n <workflow_name>
```

#### Optional metadata flags
```
--product <name>
--stage <stage>
--version <version>
--service <service>
--from-stage <stage>
--to-stage <stage>
--notification-type <deployment|service-update|stage-transition|release|hotfix>
```

If no deployment metadata is provided, the tool falls back to the legacy
long/short templates.

## License

Copyright (C) 2021-2022 Jaspar Stach

Licensed under the [GNU General Public License v3.0 or later](LICENSE).
