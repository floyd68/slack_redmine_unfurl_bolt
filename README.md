# slack_redmine_unfurl_bolt
unfurl private redmine link for slack using bolt python

#slack #redmine #slackeventsapi #unfurl #html2text #bolt

## Installation

### Create Slack App

https://api.slack.com/apps/

#### Initial Parameters
```
{
    "display_information": {
        "name": "Redmine unfurler"
    },
    "settings": {
        "org_deploy_enabled": false,
        "socket_mode_enabled": true,
        "is_hosted": false,
        "token_rotation_enabled": false
    }
}
```

#### OAuth & Permissions

In `Bot Token Scopes` Add

- chat:write
- links:read
- links:write
- users:read.email

#### Event Subscriptions

Check `Enable Events` On

In `Subscribe to bot events`, Add link_shared

### On-Premise server side setup

clone from https://github.com/floyd68/slack_redmine_unfurl_bolt.git
eg) /var/slack_redmine_bolt

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

create environment config `/etc/slack_redmine_bolt.conf`
```
REDMINE_URL=http://your_redmine_url
REDMINE_API_KEY=readmine api key from http://redmine_url/my/account
SLACK_BOT_TOKEN=xoxb-xxxxxx...
SLACK_APP_TOKEN=xapp-1-xxxxx...
```

create systemd service file `/etc/systemd/system/slack_unfurler.service`
```
[Unit]
Description=Slack Redmine unfurler
After=syslog.target network.target

[Service]
Type=simple
User=http
EnvironmentFile=/etc/slack_redmine_bolt.conf
WorkingDirectory=/var/slack_redmine_bolt
ExecStart=/var/slack_redmine_bolt/.venv/bin/python app.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

register and run with systemd
```
systemctl enable --now slack_unfurler.service
```
