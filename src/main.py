import os
import re

from helper import helperfunc,helper_button_actions
from tv import tv_req

from slack_bolt import App
from dotenv import load_dotenv


load_dotenv()
app = App(
    token = os.getenv('SLACK_BOT_TOKEN'),
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
)
#CHAT = app.client.chat_postMessage()

@app.command("/help")
def help(ack,body,logger):
    helperfunc(ack,body)

@app.action(re.compile("helper_button$"))
def handle_helper_button(ack, body, logger):
    helper_button_actions(ack,body)


@app.command("/requesttv")
def tvreq(ack,body,logger):
    tv_req(ack,body)

@app.action(re.compile("^tv_request_button\d+$"))
def handle_tv_request_button(ack, body, logger):
    ack()
    app.client.chat_postMessage(
        channel=body['user']['id'],
        text="You selected: " + body['actions'][0]['value']
    )


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3001)))