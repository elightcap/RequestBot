import requests
import os
import requests
import random
import string
import json

from dotenv import load_dotenv
from slack_bolt import App

load_dotenv()


app = App(
    token = os.getenv('SLACK_BOT_TOKEN'),
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
)

ADMIN_ID = os.getenv('SLACK_ADMIN_ID')
JELLYFIN_API_KEY = os.getenv('JELLYFIN_API_KEY')
JELLYFIN_URL = os.getenv('JELLYFIN_URL')
JELLYFIN_HEADERS = {"X-Emby-Authorization": "Mediabrowser Token=" + JELLYFIN_API_KEY, "Content-Type": "application/json"}

def invite_req(ack,body):
    ack()
    try:
        text = body['text']
        inviteMsg = f"<@{body['user_id']}> has requested an invite! Email: {text}"
        mBlocks = [{
        "type": "actions",
        "block_id": "invite_request_actions",
        "elements": [
            {
                "type": "button",
                "action_id": "invite_approve_button",
                "text": {
                    "type": "plain_text",
                    "text": "Approve",
                    "emoji": True
                },
                "value": text
            },
            {
                "type": "button",
                "action_id": "invite_deny_button",
                "text": {
                    "type": "plain_text",
                    "text": "Deny",
                    "emoji": True
                },
                "value": "deny"
            }
        ]
    }]
        app.client.chat_postMessage(
            channel=ADMIN_ID,
            text=inviteMsg
    )

        app.client.chat_postMessage(
            channel=ADMIN_ID,
            text=inviteMsg,
            blocks=mBlocks
        )
    except KeyError as e:
        print(e)
        app.client.chat_postMessage(
            channel=body['user_id'],
            text="Please enter your email address to invite!"
        )
        return


def invite_approve_actions(ack,body):
    ack()
    email = body['actions'][0]['value']
    msg = body['message']['text']
    split = msg.split(" ")
    user = split[0]
    user = user.replace("<@", "").replace(">", "")
    N=12
    pw = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
    jfinBody = {"Name": email, "Password": pw}
    jfinJson = json.dumps(jfinBody)
    jfin_url = JELLYFIN_URL + "/Users/New"
    jfinReq = requests.post(jfin_url, data=jfinJson, headers=JELLYFIN_HEADERS)
    app.client.chat_postMessage(
        channel=ADMIN_ID,
        text="Approved!"
    )
    app.client.chat_postMessage(
        channel=user,
        text=f"Your request has been approved! please login to {JELLYFIN_URL} with the following credentials: \n Username: {email} \n Password: {pw} \n Please change your password after logging in."
    )


def invite_deny_actions(ack,body):
    ack()
    msg= body['message']['text']
    split = msg.split(" ")
    user = split[0]
    user = user.replace("<@", "").replace(">", "")
    app.client.chat_postMessage(
        channel=ADMIN_ID,
        text="Denied!"
    )
    app.client.chat_postMessage(
        channel=user,
        text="Sorry, your request has been denied.  Please message the admin if you have any questions."
    )