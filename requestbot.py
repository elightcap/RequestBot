import os
import urllib.parse
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
ombi_movie_url = "https://ombi.elightcap.com/api/v1/Request/movie"
ombi_tv_url = "https://ombi.elightcap.com/api/v2/Requests/tv"
bot_id = None
print(os.getenv('SLACK_BOT_TOKEN'))

MOVIE_COMMAND = "requestmovie"
TV_COMMAND = "requesttv"

@app.message(MOVIE_COMMAND)
async def request_movie(message, say):
    print(message)
    messageText = ((message['text']).replace(MOVIE_COMMAND, "")).strip()
    movieUrlEncode = urllib.parse.quote(messageText)
    dbReqURL = movie_url + movieUrlEncode
    dbReq = requests.get(dbReqURL, headers=moviedb_headers)
    dbReqJson = json.loads(dbReq.text)
    if(len(dbReqJson['results']) > 1):
        count = len(dbReqJson['results'])
        blocks = [{
            "type": "actions",
            "block_id": "movie_request_actions",
            "elements": []
        }]
        for i in range(count):
            id = str(dbReqJson['results'][i]['id']).strip()
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
        print(blocks)
        await say(
            blocks=blocks,
        )
        return
    movieID = (dbReqJson['results'][0]['id'])
    print(movieID)
    movieName = dbReqJson['results'][0]['title']
    ombiBody = {"theMovieDbId": movieID, "languageCode": "EN", "is4kRequest": False}
    ombiJson = json.dumps(ombiBody)
    ombiReq = requests.post(ombi_movie_url, data=ombiJson, headers=ombi_headers)
    ombiMovieLink = "https://ombi.elightcap.com/details/movie/" + str(movieID)
    await say(f"Requesting <{ombiMovieLink}|{movieName}>!")

@app.message(TV_COMMAND)
async def request_tv(message, say):
    messageText = ((message['text']).replace(TV_COMMAND, "")).strip()
    tvUrlEncode = urllib.parse.quote(messageText)
    dbReqURL = tv_url + tvUrlEncode
    dbReq = requests.get(dbReqURL, headers=moviedb_headers)
    dbReqJson = json.loads(dbReq.text)
    tvID = (dbReqJson['results'][0]['id'])
    tvName = dbReqJson['results'][0]['name']
    ombiBody = {"theMovieDbId": tvID, "requestAll": True, "latestSeason": True, "firstSeason": True}
    ombiJson = json.dumps(ombiBody)
    print(ombiBody)
    ombiReq = requests.post(ombi_tv_url, data=ombiJson, headers=ombi_headers)
    print(ombiReq.text)
    ombiTVLink = "https://ombi.elightcap.com/details/tv/" + str(tvID)
    await say(f"Requesting <{ombiTVLink}|{tvName}>!")

@app.event("app_mention")
async def app_mention(event, say):
    messageText = event['text']
    messageText = (messageText.replace("<@U039Y3P5SQH>", "")).strip()
    messageJson = {"text": messageText}
    print(messageJson)
    if TV_COMMAND in messageText:
        await request_tv(messageJson, say)
    elif MOVIE_COMMAND in messageText:
        await request_movie(messageJson, say)
list = [*range(1, 10)]

@app.action("button")
async def handle_action(ack, body, logger, say):
    await ack()
    print(body)
    movieID = body['actions'][0]['value']
    movieName = body['actions'][0]['text']['text']
    ombiBody = {"theMovieDbId": movieID, "languageCode": "EN", "is4kRequest": False}
    ombiJson = json.dumps(ombiBody)
    ombiReq = requests.post(ombi_movie_url, data=ombiJson, headers=ombi_headers)
    ombiMovieLink = "https://ombi.elightcap.com/details/movie/" + str(movieID)
    await say(f"Requesting <{ombiMovieLink}|{movieName}>!")

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3001)))
