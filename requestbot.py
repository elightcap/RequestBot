from email import message
import os
import urllib.parse
from pyparsing import empty
import requests
import json
import re
import random
import string

from slack_bolt import App
from slack_bolt.async_app import AsyncApp
from dotenv import load_dotenv


load_dotenv()
app = App(
    token = os.getenv('SLACK_BOT_TOKEN'),
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
)

moviedb_api_key = os.getenv('MOVIEDB_API_KEY')
moviedb_headers = {'Authorization': f'Bearer {moviedb_api_key}'}
movie_url = "https://api.themoviedb.org/4/search/movie?query="
tv_url = "https://api.themoviedb.org/4/search/tv?query="
ombi_api_key = os.getenv('OMBI_API_KEY')
ombi_headers = {"ApiKey": ombi_api_key, "Content-Type": "application/json"}
ombi_base_url = os.getenv('OMBI_BASE_URL')
ombi_movie_url = ombi_base_url + "/api/v1/Request/movie"
ombi_tv_url = ombi_base_url + "/api/v2/Requests/tv"
jellyfin_api_key = os.getenv('JELLYFIN_API_KEY')
jellyfin_url = os.getenv('JELLYFIN_URL')
jellyfin_headers = {"X-Emby-Authorization": "Mediabrowser Token=" + jellyfin_api_key, "Content-Type": "application/json"}
bot_id = None

MOVIE_COMMAND = "requestmovie"
TV_COMMAND = "requesttv"

@app.message(MOVIE_COMMAND)
def request_movie(message, say):
    messageText = ((message['text']).replace(MOVIE_COMMAND, "")).strip()
    movieUrlEncode = urllib.parse.quote(messageText)
    dbReqURL = movie_url + movieUrlEncode
    dbReq = requests.get(dbReqURL, headers=moviedb_headers)
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
        ombiReq = requests.post(ombi_movie_url, data=ombiJson, headers=ombi_headers)
        ombiMovieLink = ombi_base_url + "/details/movie/" + str(movieID)
        say(f"Requesting <{ombiMovieLink}|{movieName}>!")

@app.message(TV_COMMAND)
def request_tv(message, say):
    messageText = ((message['text']).replace(TV_COMMAND, "")).strip()
    tvUrlEncode = urllib.parse.quote(messageText)
    dbReqURL = tv_url + tvUrlEncode
    dbReq = requests.get(dbReqURL, headers=moviedb_headers)
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
        ombiReq = requests.post(ombi_tv_url, data=ombiJson, headers=ombi_headers)
        ombiTVLink = ombi_base_url + "/details/tv/" + str(tvID)
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
    responseURL = body['response_url']
    response = requests.post(responseURL)
    ack()
    movieID = body['actions'][0]['value']
    movieName = body['actions'][0]['text']['text']
    ombiBody = {"theMovieDbId": movieID, "languageCode": "EN", "is4kRequest": False}
    ombiJson = json.dumps(ombiBody)
    ombiReq = requests.post(ombi_movie_url, data=ombiJson, headers=ombi_headers)
    ombiMovieLink = ombi_base_url + "/details/movie/" + str(movieID)
    say(f"Requesting <{ombiMovieLink}|{movieName}>!")

@app.action(re.compile("^tv_request_button\d+$"))
def handle_tv_button(ack, body, say):
    responseUrl = body['response_url']
    response = requests.post(responseUrl)
    ack()
    tvID = body['actions'][0]['value']
    tvName = body['actions'][0]['text']['text']
    ombiBody = {"theMovieDbId": tvID, "requestAll": True, "latestSeason": True, "firstSeason": True}
    ombiJson = json.dumps(ombiBody)
    ombiReq = requests.post(ombi_tv_url, data=ombiJson, headers=ombi_headers)
    ombiMovieLink = ombi_base_url + "/details/tv/" + str(tvID)
    say(f"Requesting <{ombiMovieLink}|{tvName}>!")

@app.command("/requestmovie")
def handle_movie_command(ack, body, logger, say):
    ack()
    text = body['text']
    messageJson = {"text": text}
    request_movie(messageJson, say)

@app.command("/requesttv")
def handle_tv_command(ack, body, logger, say):
    ack()
    text = body['text']
    messageJson = {"text": text}
    request_tv(messageJson, say)

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
        channel="UERHVSNFL",
        text=inviterequest
    )

    app.client.chat_postMessage(
        channel="UERHVSNFL",
        text=inviterequest,
        blocks=mBlocks
    )

@app.action("invite_approve_button")
def handle_invite_approve_button(ack, body, say):
    ack()
    email = body['actions'][0]['value']
    msg= body['message']['text']
    split = msg.split(" ")
    user = split[0]
    user = user.replace("<@", "").replace(">", "")
    N=12
    pw = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
    jfinBody = {"Name": email, "Password": pw}
    jfinJson = json.dumps(jfinBody)
    jfin_url = jellyfin_url + "/Users/New"
    jfinReq = requests.post(jfin_url, data=jfinJson, headers=jellyfin_headers)
    say("Approved!")
    app.client.chat_postMessage(
        channel=user,
        text=f"Your request has been approved! please login to {jellyfin_url} with the following credentials: \n Username: {email} \n Password: {pw} and change your password after logging in."
    )

@app.action("invite_deny_button")
def handle_invite_deny_button(ack, body, say):
    ack()
    msg= body['message']['text']
    split = msg.split(" ")
    user = split[0]
    user = user.replace("<@", "").replace(">", "")
    say("Denied!")
    app.client.chat_postMessage(
        channel=user,
        text="Sorry, your request has been denied.  Please message the admin if you have any questions."
    )


@app.message(re.compile("(^help$)"))
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
