import requests
import json
from slacker import Slacker
import logging
import os

print('Loading function... ')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def to_markdown(channels):
    header = u"""
# Introduction
[mohikanz](https://mohikanz.slack.com) は、[究極のIT系最新技術情報収集用Slackチーム公開 - モヒカンSlack -]()
にて紹介されているSlackチーム、mohikan から派生した雑談用 Slack チームです。
mohikanz はエンジニアがエンジニアリングのみならず、様々な話題についてわいわい話すことができるコミュニティです！

- 社内でエンジニアが少なくて情報共有ができない！
- エンジニアのコミュニティに入ってみたいけど何から手を付けたら良いかわからない！

と思っている人に、雑談からエンジニアのコミュニティへの入り口を提供しています。

入りたいと思った方はこちらへどうぞ！
https://mohikanz-invitation.herokuapp.com

# Slack Channel List

毎日 5 時に自動更新しています。


Name | Topic | Persons
----- | ----- | -------
"""

    body = []
    for c in channels:
        elems = [
                "[#%s](https://mohikanz.slack.com/messages/%s)" % (c["name"], c["name"]),
                c["topic"]["value"],
                str(c["num_members"])
        ]
        elems = [e.replace("\n", "<br>") for e in elems]
        body.append(" | ".join(elems))
    return header + "\n".join(body)

def slack_channels():
    slack = Slacker(SLACK_TOKEN)
    response = slack.channels.list(exclude_archived=1)
    channels = response.body['channels']
    return channels

def edit_gist(content):
    headers = {'Authorization': 'token %s' % GITHUB_TOKEN}
    data= {
            "description": "Channels list of the mohikanz Slack( https://mohikanz.slack.com )",
            'files': {
                'channels.md': {
                    'content': content
                    }
                }
            }
    jdata = json.dumps(data)
    res=requests.patch(ENDPOINT, jdata,headers=headers)

def handler(event, context):
    # Get Global Value
    global SLACK_TOKEN
    global GIST_ID
    global ENDPOINT
    global GITHUB_TOKEN
    SLACK_TOKEN = os.environ['SLACK_TOKEN']
    GIST_ID = os.environ['GIST_ID']
    ENDPOINT = 'https://api.github.com/gists/%s' % GIST_ID
    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

    # 受信したjsonをLogsに出力
    logging.info(json.dumps(event))
    channels = slack_channels()
    content = to_markdown(channels)
    edit_gist(content)
