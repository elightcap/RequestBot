import os
import random
import string
import json
from urllib.error import HTTPError
import requests

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
JELLYFIN_HEADERS = {
    "X-Emby-Authorization": "Mediabrowser Token=" + JELLYFIN_API_KEY,
    "Content-Type": "application/json"
    }
PW_NUMBER = 12


def invite_req(ack,body):
    """function handles invite request.  Sends button to admin for approval"""
    ack()
    try:
        text = body['text']
        invite_msg = f"<@{body['user_id']}> has requested an invite! Email: {text}"
        m_blocks = [{
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
            text=invite_msg
    )

        app.client.chat_postMessage(
            channel=ADMIN_ID,
            text=invite_msg,
            blocks=m_blocks
        )
    except KeyError as error:
        print(error)
        app.client.chat_postMessage(
            channel=body['user_id'],
            text="Please enter your email address to invite!"
        )
        return


def invite_approve_actions(ack,body):
    """function handles invite approval.  If approved, creates user in jellyfin and sends invite"""
    ack()
    email = body['actions'][0]['value']
    msg = body['message']['text']
    split = msg.split(" ")
    user = split[0]
    user = user.replace("<@", "").replace(">", "")
    p_w = ''.join(random.choices(string.ascii_uppercase + string.digits, k=PW_NUMBER))
    jfin_body = {"Name": email, "Password": p_w}
    jfin_json = json.dumps(jfin_body)
    jfin_url = JELLYFIN_URL + "/Users/New"
    try:
        requests.post(jfin_url, data=jfin_json, headers=JELLYFIN_HEADERS)
    except HTTPError as err:
        print(err)
        return
    app.client.chat_postMessage(
        channel=ADMIN_ID,
        text="Approved!"
    )
    app.client.chat_postMessage(
        channel=user,
        text=f"""Your request has been approved!
         please login to {JELLYFIN_URL} with the following credentials: 
        \n Username: {email} \n Password: {p_w} \n Please change your password after logging in."""
    )


def invite_deny_actions(ack,body):
    """function handles invite denial.  Sends message to user that invite was denied"""
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
        text="""Sorry, your request has been denied.
         Please message the admin if you have any questions."""
    )
    