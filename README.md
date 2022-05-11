# mattermost-notify

This tool is desired to post messages to a mattermost channel.
You will need a mattermost webhook URL and give a channel name.

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

Print a github workflow status:
```
mnotify-git <hook_url> <channel> -S [success, failure] -r <orga/repo> -b <branch> -w <workflow_id> -n <workflow_name>
```

## License

Copyright (C) 2021-2022 Jaspar Stach

Licensed under the [GNU General Public License v3.0 or later](LICENSE).