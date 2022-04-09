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

MOVIE_DB_API_KEY = os.getenv('MOVIEDB_API_KEY')
MOVIE_DB_HEADERS = {'Authorization': f'Bearer {MOVIE_DB_API_KEY}'}
MOVIE_URL = "https://api.themoviedb.org/4/search/movie?query="
OMBI_API_KEY = os.getenv('OMBI_API_KEY')
OMBI_HEADERS = {"ApiKey": OMBI_API_KEY, "Content-Type": "application/json"}
OMBI_BASE_URL = os.getenv('OMBI_BASE_URL')
OMBI_MOVIE_URL = OMBI_BASE_URL + "/api/v1/Request/movie"

def movie_req(ack,body):
    """movie request function.  If more than one result, have user select correct.
    If only one result, request movie."""
    ack()
    print(body)
    try:
        text = body['text']
        movie_url_encode = urllib.parse.quote(text)
        db_req_url = MOVIE_URL + movie_url_encode
        db_req = requests.get(db_req_url, headers=MOVIE_DB_HEADERS)
        db_req_json = json.loads(db_req.text)
        if len(db_req_json['results']) > 1:
            count = len(db_req_json['results'])
            blocks = [{
                "type": "actions",
                "block_id": "movie_request_actions",
                "elements": []
            }]
            for i in range(count):
                i_id = str(db_req_json['results'][i]['id']).strip()
                if len(db_req_json['results'][i]['title']) < 76:
                    blocks[0]['elements'].append({
                        "type":"button",
                        "action_id": "movie_request_button"+str(i),
                        "text": {
                            "type": "plain_text",
                            "text": db_req_json['results'][i]['title'],
                            "emoji": True
                        },
                        "value": i_id
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
    except KeyError as error:
        print(error)
        app.client.chat_postMessage(
            channel=body['user_id'],
            text="Please enter a movie title!"
        )
        return

def movie_button_actions(ack,body):
    """movie button actions function.  Sends movie request to Ombi based on button value."""
    ack()
    response_url = body['response_url']
    movie_id = body['actions'][0]['value']
    movie_name = body['actions'][0]['text']['text']
    ombi_body = {"theMovieDbId": movie_id, "languageCode": "EN", "is4kRequest": False}
    ombi_json = json.dumps(ombi_body)
    try:
        requests.post(OMBI_MOVIE_URL, headers=OMBI_HEADERS, json=ombi_json)
    except HTTPError as err:
        print(err)
        app.client.chat_postMessage(
            channel=body['user_id'],
            text="There was an error with your request.  Please try again."
        )
        return
    ombi_movie_link = OMBI_BASE_URL + "/details/movie/" + str(movie_id)
    app.client.chat_postMessage(
        channel=body['user']['id'],
        text=f"Requesting <{ombi_movie_link}|{movie_name}>!"
    )
    del_body = {"delete_original": "true"}
    body_json = json.dumps(del_body)
    try:
        requests.post(response_url, data=body_json)
    except HTTPError as err:
        print(err)
        return
