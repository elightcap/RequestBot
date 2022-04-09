import os
import requests
import json
import urllib.parse

from dotenv import load_dotenv
from slack_bolt import App

load_dotenv()
app = App(
    token = os.getenv('SLACK_BOT_TOKEN'),
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
)

MOVIE_DB_API_KEY = os.getenv('MOVIEDB_API_KEY')
MOVIE_DB_HEADERS = {'Authorization': f'Bearer {MOVIE_DB_API_KEY}'}
MOVIE_URL = "https://api.themoviedb.org/4/search/movie?query="
OMBI_API_KEY = os.getenv('OMBI_API_KEY')
OMBI_HEADERS = {"ApiKey": OMBI_API_KEY, "Content-Type": "application/json"}
OMBI_BASE_URL = os.getenv('OMBI_BASE_URL')
OMBI_MOVIE_URL = OMBI_BASE_URL + "/api/v1/Request/movie"

def movie_req(ack,body):
    ack()
    print(body)
    try:
        text = body['text']
        movieUrlEncode = urllib.parse.quote(text)
        dbReqUrl = MOVIE_URL + movieUrlEncode
        dbReq = requests.get(dbReqUrl, headers=MOVIE_DB_HEADERS)
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
                if(len(dbReqJson['results'][i]['title']) < 76):
                    blocks[0]['elements'].append({
                        "type":"button",
                        "action_id": "movie_request_button"+str(i),
                        "text": {
                            "type": "plain_text",
                            "text": dbReqJson['results'][i]['title'],
                            "emoji": True
                        },
                        "value": id
                    })
            app.client.chat_postMessage(
                channel=body['user_id'],
                text="Please Select a Movie:"
                )
            app.client.chat_postMessage(
                channel=body['user_id'],
                blocks=blocks,
                text="Select a Movie to request!"
            )
            return
    except KeyError as e:
        print(e)
        app.client.chat_postMessage(
            channel=body['user_id'],
            text="Please enter a movie title!"
        )
        return

def movie_button_actions(ack,body):
    ack()
    responseUrl = body['response_url']
    movieID = body['actions'][0]['value']
    movieName = body['actions'][0]['text']['text']
    ombiBody = {"theMovieDbId": movieID, "languageCode": "EN", "is4kRequest": False}
    ombiJson = json.dumps(ombiBody)
    ombiReq = requests.post(OMBI_MOVIE_URL, headers=OMBI_HEADERS, json=ombiJson)
    ombiMovieLink = OMBI_BASE_URL + "/details/movie/" + str(movieID)
    app.client.chat_postMessage(
        channel=body['user']['id'],
        text=f"Requesting <{ombiMovieLink}|{movieName}>!"
    )
    delBody = {"delete_original": "true"}
    bodyJson = json.dumps(delBody)
    delReq = requests.post(responseUrl, data=bodyJson)
