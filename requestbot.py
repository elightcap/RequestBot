import os
import urllib.parse
import requests
import json
import re
import random
import string

from slack_bolt import App
from dotenv import load_dotenv



load_dotenv()
app = App(
    token = os.getenv('SLACK_BOT_TOKEN'),
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
)

MOVIEDB_API_KEY = os.getenv('MOVIEDB_API_KEY')
MOVIEDB_HEADERS = {'Authorization': f'Bearer {MOVIEDB_API_KEY}'}
MOVIE_URL = "https://api.themoviedb.org/4/search/movie?query="
TV_URL = "https://api.themoviedb.org/4/search/tv?query="
OMBI_API_KEY = os.getenv('OMBI_API_KEY')
OMBI_HEADERS = {"ApiKey": OMBI_API_KEY, "Content-Type": "application/json"}
OMBI_BASE_URL = os.getenv('OMBI_BASE_URL')
OMBI_MOVIE_URL = OMBI_BASE_URL + "/api/v1/Request/movie"
OMBI_TV_URL = OMBI_BASE_URL + "/api/v2/Requests/tv"
JELLYFIN_API_KEY = os.getenv('JELLYFIN_API_KEY')
JELLYFIN_URL = os.getenv('JELLYFIN_URL')
JELLYFIN_HEADERS = {"X-Emby-Authorization": "Mediabrowser Token=" + JELLYFIN_API_KEY, "Content-Type": "application/json"}
ADMIN_ID = os.getenv('SLACK_ADMIN_ID')
bot_id = None

MOVIE_COMMAND = "requestmovie"
TV_COMMAND = "requesttv"

@app.message(re.compile(MOVIE_COMMAND, re.IGNORECASE))
def request_movie(message, say):
    messageText = ((message['text']).replace(MOVIE_COMMAND, "")).strip()
    movieUrlEncode = urllib.parse.quote(messageText)
    dbReqURL = MOVIE_URL + movieUrlEncode
    dbReq = requests.get(dbReqURL, headers=MOVIEDB_HEADERS)
    dbReqJson = json.loads(dbReq.text)
    if(len(dbReqJson['results']) > 1):
        count = len(dbReqJson['results'])
        if count < 4:
            count = count
        else:
            count = 4
        blocks = [{
            "type": "actions",
            "block_id": "movie_request_actions",
            "elements": []
        }]
        for i in range(0,count):
            id = str(dbReqJson['results'][i]['id']).strip()
            if(len(dbReqJson['results'][i]['title']) < 76):
                blocks[0]['elements'].append({
                    "type": "button",
                    "action_id": "movie_request_button"+str(i),
                    "text": {
                        "type": "plain_text",
                        "text": dbReqJson['results'][i]['title'],
                        "emoji": True
                    },
                    "value": id
                })
        if(message["channel_name"] == "directmessage"):
            app.client.chat_postMessage(
                channel=message["user_id"],
                blocks=blocks,
                text="Please select a movie to request"
            )
        else:
            say("Please select a movie:")
            say(
                blocks=blocks,
                text="Please select the movie you would like to request"
            )
        return
    else:
        movieID = (dbReqJson['results'][0]['id'])
        movieName = dbReqJson['results'][0]['title']
        ombiBody = {"theMovieDbId": movieID, "languageCode": "EN", "is4kRequest": False}
        ombiJson = json.dumps(ombiBody)
        ombiReq = requests.post(OMBI_MOVIE_URL, data=ombiJson, headers=OMBI_HEADERS)
        ombiMovieLink = OMBI_BASE_URL + "/details/movie/" + str(movieID)
        if(message["channel_name"] == "directmessage"):
            app.client.chat_postMessage(
                channel=message["user_id"],
                text=f"Requesting <{ombiMovieLink}|{movieName}>!"
            )
        else:
            say(f"Requesting <{ombiMovieLink}|{movieName}>!")

@app.message(re.compile(TV_COMMAND, re.IGNORECASE))
def request_tv(message, say):
    messageText = ((message['text']).replace(TV_COMMAND, "")).strip()
    tvUrlEncode = urllib.parse.quote(messageText)
    dbReqURL = TV_URL + tvUrlEncode
    dbReq = requests.get(dbReqURL, headers=MOVIEDB_HEADERS)
    dbReqJson = json.loads(dbReq.text)
    if(len(dbReqJson['results']) > 1):
        count = len(dbReqJson['results'])
        if count < 4:
            count = count
        else:
            count = 4
        blocks = [{
            "type": "actions",
            "block_id": "tv_request_actions",
            "elements": []
        }]
        for i in range(count):
            id = str(dbReqJson['results'][i]['id']).strip()
            if(len(dbReqJson['results'][i]['name']) < 76):
                blocks[0]['elements'].append({
                    "type":"button",
                    "action_id": "tv_request_button"+str(i),
                    "text": {
                        "type": "plain_text",
                        "text": dbReqJson['results'][i]['name'],
                        "emoji": True
                    },
                    "value": id
                })
        if(message["channel_name"] == "directmessage"):
            app.client.chat_postMessage(
                channel=message["user_id"],
                blocks=blocks,
                text="Please select a TV show to request"
            )
        else:     
            say("Please Select a Show:")
            say(
                blocks=blocks,
                text="Select a TV show to request!"
            )
        return
    else:
        tvID = (dbReqJson['results'][0]['id'])
        tvName = dbReqJson['results'][0]['name']
        ombiBody = {"theMovieDbId": tvID, "requestAll": True, "latestSeason": True, "firstSeason": True}
        ombiJson = json.dumps(ombiBody)
        ombiReq = requests.post(OMBI_TV_URL, data=ombiJson, headers=OMBI_HEADERS)
        ombiTVLink = OMBI_BASE_URL + "/details/tv/" + str(tvID)
        if(message["channel_name"] == "directmessage"):
            app.client.chat_postMessage(
                channel=message["user_id"],
                text=f"Requesting <{ombiTVLink}|{tvName}>!"
            )
        else:
            say(f"Requesting <{ombiTVLink}|{tvName}>!")

@app.event("app_mention")
def app_mention(event, say):
    messageText = event['text']
    messageText = (messageText.replace("<@U039Y3P5SQH>", "")).strip()
    messageJson = {"text": messageText}
    if TV_COMMAND in messageText:
        request_tv(messageJson, say)
    elif MOVIE_COMMAND in messageText:
        request_movie(messageJson, say)
    elif "help" in messageText:
        print("help")
        help_message(messageText,say)
    

@app.action(re.compile("^movie_request_button\d+$"))
def handle_movie_button(ack, body, say):
    responseUrl = body['response_url']
    ack()
    body = {"delete_original": "true"}
    delReq = requests.post(responseUrl, data=body, headers="'Content-Type': 'application/json'")
    movieID = body['actions'][0]['value']
    movieName = body['actions'][0]['text']['text']
    ombiBody = {"theMovieDbId": movieID, "languageCode": "EN", "is4kRequest": False}
    ombiJson = json.dumps(ombiBody)
    ombiReq = requests.post(OMBI_MOVIE_URL, data=ombiJson, headers=OMBI_HEADERS)
    ombiMovieLink = OMBI_BASE_URL + "/details/movie/" + str(movieID)
    say(f"Requesting <{ombiMovieLink}|{movieName}>!")

@app.action(re.compile("^tv_request_button\d+$"))
def handle_tv_button(ack, body, say):
    responseUrl = body['response_url']
    ack()
    body = {"delete_original": "true"}
    delReq = requests.post(responseUrl, data=body, headers="'Content-Type': 'application/json'")
    tvID = body['actions'][0]['value']
    tvName = body['actions'][0]['text']['text']
    ombiBody = {"theMovieDbId": tvID, "requestAll": True, "latestSeason": True, "firstSeason": True}
    ombiJson = json.dumps(ombiBody)
    ombiReq = requests.post(OMBI_TV_URL, data=ombiJson, headers=OMBI_HEADERS)
    ombiMovieLink = OMBI_BASE_URL + "/details/tv/" + str(tvID)
    say(f"Requesting <{ombiMovieLink}|{tvName}>!")

@app.command("/requestmovie")
def handle_movie_command(ack, body, logger, say):
    ack()
    request_movie(body, say)

@app.command("/requesttv")
def handle_tv_command(ack, body, logger, say):
    ack()
    request_tv(body, say)

@app.command("/requestinvite")
def handle_invite_command(ack, body, logger, say):
    ack()
    text = body['text']
    inviterequest = f"<@{body['user_id']}> has requested an invite! Email: {text}"
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
        text=inviterequest
    )

    app.client.chat_postMessage(
        channel=ADMIN_ID,
        text=inviterequest,
        blocks=mBlocks
    )
@app.command("/help")
def handle_help_command(ack, body, logger, say):
    ack()
    help_message(body,say)

@app.action("invite_approve_button")
def handle_invite_approve_button(ack, body, say):
    ack()
    responseUrl=body['response_url']
    body = {"delete_original": "true"}
    bodyJson = json.dumps(body)
    delReq = requests.post(responseUrl, data=bodyJson)
    email = body['actions'][0]['value']
    msg= body['message']['text']
    split = msg.split(" ")
    user = split[0]
    user = user.replace("<@", "").replace(">", "")
    N=12
    pw = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
    jfinBody = {"Name": email, "Password": pw}
    jfinJson = json.dumps(jfinBody)
    jfin_url = JELLYFIN_URL + "/Users/New"
    jfinReq = requests.post(jfin_url, data=jfinJson, headers=JELLYFIN_HEADERS)
    say("Approved!")
    app.client.chat_postMessage(
        channel=user,
        text=f"Your request has been approved! please login to {JELLYFIN_URL} with the following credentials: \n Username: {email} \n Password: {pw} \n Please change your password after logging in."
    )

@app.action("invite_deny_button")
def handle_invite_deny_button(ack, body, say):
    ack()
    responseUrl=body['response_url']
    body = {"delete_original": "true"}
    bodyJson = json.dumps(body)
    delReq = requests.post(responseUrl, data=bodyJson)
    msg = body['message']['text']
    split = msg.split(" ")
    user = split[0]
    user = user.replace("<@", "").replace(">", "")
    say("Denied!")
    app.client.chat_postMessage(
        channel=user,
        text="Sorry, your request has been denied.  Please message the admin if you have any questions."
    )


@app.message(re.compile("(^help$)", re.IGNORECASE))
def help_message(message, say):
    msg = "Hi im RequestBot, a bot to help you download movies and tv shows! Please choose an option below!"

    blocks = [
        {
            "type": "actions",
            "block_id": "tv_request_actions",
            "elements": [
                {
                    "type": "button",
                    "action_id": "tv_help_button",
                    "text": {
                        "type": "plain_text",
                        "text": "TV Help",
                        "emoji": True
                    },
                    "value": "tv_help_button"
                },
                {
                    "type": "button",
                    "action_id": "movie_help_button",
                    "text": {
                        "type": "plain_text",
                        "text": "Movie Help",
                        "emoji": True
                    },
                    "value": "movie_help_button"
                }
            ]
        }]
    say(f"{msg}")
    say(
        blocks=blocks, text="Select an option!"
        )

@app.action("tv_help_button")
def tv_help_button(ack, body, say):
    ack()
    help_tv(body, say)

@app.action("movie_help_button")
def movie_help_button(ack, body, say):
    ack()
    help_movie(body, say)

@app.message("help movie")
def help_movie(message, say):
    msg1 = "To request a movie, just type `requestmovie` followed by the name of the movie you want to request! For example, `requestmovie The Matrix`. You can also just mention me in any channel and I'll try to find the movie for you, for example `@RequestBot The Matrix`"
    msg2 = "Slash commands are also supported, for example `/requestmovie The Matrix`"
    say(f"{msg1}")
    say(f"{msg2}")

@app.message("help tv")
def help_tv(message, say):
    msg1 = "To request a tv show, just type `requesttv` followed by the name of the tv show you want to request! For example, `requesttv The Simpsons`. You can also just mention me in any channel and I'll try to find the tv show for you, for example `@RequestBot The Simpsons`"
    msg2 = "Slash commands are also supported, for example `/requesttv The Simpsons`"
    say(f"{msg1}")
    say(f"{msg2}")

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3001)))