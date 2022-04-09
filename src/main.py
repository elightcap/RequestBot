import os
import re

from helper import helperfunc,helper_button_actions
from tv import tv_req,tv_button_actions
from movie import movie_req,movie_button_actions
from invite import invite_req,invite_approve_actions,invite_deny_actions

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
    tv_button_actions(ack,body)

@app.command("/requestmovie")
def moviereq(ack,body,logger):
    movie_req(ack,body)

@app.action(re.compile("^movie_request_button\d+$"))
def handle_movie_request_button(ack, body, logger):
    movie_button_actions(ack,body)

@app.command("/requestinvite")
def invitereq(ack,body,logger):
    invite_req(ack,body)

@app.action("invite_approve_button")
def handle_invite_approve_button(ack, body, logger):
    invite_approve_actions(ack,body)

@app.action("invite_deny_button")
def handle_invite_deny_button(ack, body, logger):
    invite_deny_actions(ack,body)


@app.event("message")
def handle_message_events(body, logger):
    return

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3001)))