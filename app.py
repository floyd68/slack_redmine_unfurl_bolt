import os
import re
from html2text import HTML2Text
from redminelib import Redmine
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from urllib.parse import urlparse
import logging
import sys

REDMINE_URL = os.environ['REDMINE_URL']
REDMINE_API_KEY = os.environ['REDMINE_API_KEY']
                 
redmine = Redmine(REDMINE_URL, key=REDMINE_API_KEY)

logging.basicConfig(level=logging.DEBUG)

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
slack_client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

REGEX_REPLACE = (
  (re.compile('^- ', flags=re.M), '• '),
  (re.compile('^  - ', flags=re.M), '  ◦ '),
  (re.compile('^    - ', flags=re.M), '    ⬩ '), # ◆
  (re.compile('^      - ', flags=re.M), '    ◽ '),
  (re.compile('^#+ (.+)$', flags=re.M), r'*\1*'),
  (re.compile('\*\*'), '*'),
)

def markdown2slack(t):
    for regex, replacement in REGEX_REPLACE:
        t = regex.sub(replacement, t)
    return t
    
def contents_issue(url, paths):
    try:
        issue = redmine.issue.get(paths[2])
    except Exception as e:
        print(f"Exception {e=}, {type(e)=}")
        print("Issue not found : " + paths[2])
        return { "title" : "DIVERSE Redmine", "text" : "존재하지 않는 이슈입니다" }

    user = redmine.user.get(issue.assigned_to.id)
    author = redmine.user.get(issue.author.id)

    h = HTML2Text()
    h.ignore_links = True
    description = h.handle(issue.description)

    if "created_on" in dir(issue):
        create_date = " 이(가) " + issue.created_on.strftime("%Y/%m/%d") + "에 생성"
    else:
        create_date = ""

    if hasattr(issue, 'due_date') and issue.due_date is not None:
        due_date = issue.due_date.strftime("%Y/%m/%d")
    else:
        due_date = "없음"

    content = {
        "title" : issue.project.name + " #" + paths[2] + " " + issue.subject,
        "title_link" : url,
        "color" : "#7cd197",
        "author_name" : issue.author.name + create_date,
        "fields" : [
            { "title" : "담당자",   "value" : issue.assigned_to.name,  "short" : False },
            { "title" : "상태",     "value" : issue.status.name, "short" : True },
            { "title" : "우선순위", "value" : issue.priority.name, "short" : True },
            { "title" : "시작시간", "value" : issue.start_date.strftime("%Y/%m/%d"), "short" : True},
            { "title" : "완료기한", "value" : due_date, "short" : True }
        ],
        "text" : markdown2slack(description) + "\n\n",
        "footer" : "DIVERSE Redmine"
    }
    return content

def contents_version(url, paths):
    try:
        version = redmine.version.get(paths[2])
    except:
        print("Version not found : " + paths[2])
        return { "title" : "DIVERSE Redmnine", "text" : "존재하지 않는 버젼입니다" }

    h = HTML2Text()
    h.ignore_links = True
    description = h.handle(issue.description)

    content = {
            "title" : version.project.name + " @" + version.name,
            "title_link" : url,
            "color" : "#7c97d1",
            "text" : markdown2slack(description),
            "fields" : [
                { "title" : "상태", "value" : version.status, "short" : True },
                { "title" : "완료기한", "value" : version.due_date.strftime("%Y/%m/%d"), "short" : True }
            ]
    }

    return content


def parse_url(url):
    parsed = urlparse(url)

    paths = parsed.path.split('/')

#    if parsed.netloc == "redmine.w3.com" and paths[1] == "issues":
    if paths[1] == "issues":
        return contents_issue(url, paths)
    elif paths[1] == "versions":
        return contents_version(url, paths)
    else:
        return ""

@app.event("link_shared")
def message_link(body, say, logger):
    message = body["event"]
    channel = message["channel"]
    message_ts = message["message_ts"]

    unfurls = {}

    for link in message["links"]:
        url = link["url"]
        unfurls[url] = parse_url(url)

    result = slack_client.api_call(
            api_method='chat.unfurl',
            json={'channel': channel, 'ts':message_ts, 'unfurls': unfurls}
    )


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
