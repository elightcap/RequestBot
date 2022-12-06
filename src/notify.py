import os
import json
import urllib.parse
from urllib.error import HTTPError
import requests

from dotenv import load_dotenv
from slack_bolt import App

load_dotenv()
app = App(
    token = os.getenv('SLACK_BOT_TOKEN'),
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
)

def send_slack_notification(alias,name):
    app.client.chat_postMessage(
        channel=body['user']['id'],
        text=f"Your request for {alias} has been completed!"
    )