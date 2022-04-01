import os
import urllib.parse
from pyparsing import empty
import requests
import json
import re

from slack_bolt import App
from slack_bolt.async_app import AsyncApp
from dotenv import load_dotenv


load_dotenv()
app = AsyncApp(
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
bot_id = None

MOVIE_COMMAND = "requestmovie"
TV_COMMAND = "requesttv"

@app.message(MOVIE_COMMAND)
async def request_movie(message, say):
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
        await say(
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
        await say(f"Requesting <{ombiMovieLink}|{movieName}>!")

@app.message(TV_COMMAND)
async def request_tv(message, say):
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
        await say(
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
        await say(f"Requesting <{ombiTVLink}|{tvName}>!")

@app.event("app_mention")
async def app_mention(event, say):
    messageText = event['text']
    messageText = (messageText.replace("<@U039Y3P5SQH>", "")).strip()
    messageJson = {"text": messageText}
    if TV_COMMAND in messageText:
        await request_tv(messageJson, say)
    elif MOVIE_COMMAND in messageText:
        await request_movie(messageJson, say)
    

for i in range(0, 4):
    @app.action(f"movie_request_button{i}")

    async def handle_movie_button(ack, body, say):
        await ack()
        movieID = body['actions'][0]['value']
        movieName = body['actions'][0]['text']['text']
        ombiBody = {"theMovieDbId": movieID, "languageCode": "EN", "is4kRequest": False}
        ombiJson = json.dumps(ombiBody)
        ombiReq = requests.post(ombi_movie_url, data=ombiJson, headers=ombi_headers)
        ombiMovieLink = ombi_base_url + "/details/movie/" + str(movieID)
        await say(f"Requesting <{ombiMovieLink}|{movieName}>!")

#for i in range(0,4): f"tv_request_button{i}"
@app.action(re.compile("^tv_request_button"))
async def handle_tv_button(ack, body, say):
    await ack()
    tvID = body['actions'][0]['value']
    tvName = body['actions'][0]['text']['text']
    ombiBody = {"theMovieDbId": tvID, "requestAll": True, "latestSeason": True, "firstSeason": True}
    ombiJson = json.dumps(ombiBody)
    ombiReq = requests.post(ombi_tv_url, data=ombiJson, headers=ombi_headers)
    ombiMovieLink = ombi_base_url + "/details/tv/" + str(tvID)
    await say(f"Requesting <{ombiMovieLink}|{tvName}>!")

@app.message(re.compile("(^help$)"))
async def help_message(message, say):
    msg = "Hi im RequestBot, a bot to help you download movies and tv shows! For more info, try `help tv` or `help movie`!"
    await say(f"{msg}")

@app.message("help movie")
async def help_movie(message, say):
    msg = "To request a movie, just type `requestmovie` followed by the name of the movie you want to request! For example, `requestmovie The Matrix`. You can also just mention me in any channel and I'll try to find the movie for you, for example `@RequestBot The Matrix`"
    await say(f"{msg}")

@app.message("help tv")
async def help_tv(message, say):
    msg = "To request a tv show, just type `requesttv` followed by the name of the tv show you want to request! For example, `requesttv The Simpsons`. You can also just mention me in any channel and I'll try to find the tv show for you, for example `@RequestBot The Simpsons`"
    await say(f"{msg}")

@app.event("message")
async def handle_message_events(body, logger):
    logger.info(body)

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3001)))
