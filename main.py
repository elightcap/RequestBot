import os
import re

from src.helper import helperfunc,helper_button_actions
from src.tv import tv_req,tv_button_actions
from src.movie import movie_req,movie_button_actions
from src.invite import invite_req,invite_approve_actions,invite_deny_actions
from src.onelogin import onelogin_response

from slack_bolt import App
from dotenv import load_dotenv


load_dotenv()
app = App(
    token = os.getenv('SLACK_BOT_TOKEN'),
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
)

@app.command("/help")
def req_help(ack,body):
    """listener for help function"""
    helperfunc(ack,body)

@app.action(re.compile("helper_button$"))
def handle_helper_button(ack, body):
    """listener for helper button"""
    helper_button_actions(ack,body)


@app.command("/requesttv")
def tvreq(ack,body):
    """listener for tv request function"""
    tv_req(ack,body)

@app.action(re.compile(r"^tv_request_button\d+$"))
def handle_tv_request_button(ack, body):
    """listener for tv request button"""
    tv_button_actions(ack,body)

@app.command("/requestmovie")
def moviereq(ack,body):
    """listener for movie request function"""
    movie_req(ack,body)

@app.action(re.compile(r"^movie_request_button\d+$"))
def handle_movie_request_button(ack, body):
    """listener for movie request button"""
    movie_button_actions(ack,body)

@app.command("/requestinvite")
def invitereq(ack,body):
    """listener for invite request function"""
    invite_req(ack,body)

@app.action("invite_approve_button")
def handle_invite_approve_button(ack, body):
    """listener for invite approve button"""
    invite_approve_actions(ack,body)

@app.action("invite_deny_button")
def handle_invite_deny_button(ack, body):
    """listener for invite deny button"""
    invite_deny_actions(ack,body)

@app.event("message")
def handle_onelogin(message,say):
    """listener for onelogin"""
    body = message['blocks'][0]['elements'][0]['elements'][0]['text']
    if re.match(r"onelogin | one login",body, re.IGNORECASE):
        onelogin_response(message,say)
    elif "duty" in body:
        say("fuck duty")
    else:
        return

#@app.event("message")
#def handle_message_events():
#    """listener for message events"""
#    return

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3001)))
