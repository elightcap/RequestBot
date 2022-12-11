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
TV_URL = "https://api.themoviedb.org/4/search/tv?query="
OMBI_API_KEY = os.getenv('OMBI_API_KEY')
OMBI_HEADERS = {"ApiKey": OMBI_API_KEY, "Content-Type": "application/json"}
OMBI_BASE_URL = os.getenv('OMBI_BASE_URL')
OMBI_TV_URL = OMBI_BASE_URL + "/api/v2/Requests/tv"
OMBI_SEARCH_URL = OMBI_BASE_URL + "/api/v2/Search/tv"

def tv_req(ack,body):
    """tv request function.  If more than one result, have user select correct.
    If only one result, request show."""
    ack()
    try:
        text = body['text']
        tv_url_encode = urllib.parse.quote(text)
        db_req_url = TV_URL + tv_url_encode
        db_req = requests.get(db_req_url, headers=MOVIE_DB_HEADERS)
        db_req_json = json.loads(db_req.text)
        if len(db_req_json['results']) > 1:
            count = len(db_req_json['results'])
            blocks = [{
                "type": "actions",
                "block_id": "tv_request_actions",
                "elements": []
            }]
            for i in range(count):
                i_id = str(db_req_json['results'][i]['id']).strip()
                if len(db_req_json['results'][i]['name']) < 76:
                    blocks[0]['elements'].append({
                        "type":"button",
                        "action_id": "tv_request_button"+str(i),
                        "text": {
                            "type": "plain_text",
                            "text": db_req_json['results'][i]['name'],
                            "emoji": True
                        },
                        "value": i_id
                    })
            app.client.chat_postMessage(
                channel=body['user_id'],
                text="Please Select a Show:"
                )
            app.client.chat_postMessage(
                channel=body['user_id'],
                blocks=blocks,
                text="Select a TV show to request!"
            )
            return
    except KeyError as err:
        print(err)
        app.client.chat_postMessage(
            channel=body['user_id'],
            text="Please enter a tv show name with your request"
        )
        return

def tv_button_actions(ack,body):
    """tv button actions function.  request show based on button value"""
    ack()
    response_url = body['response_url']
    tv_id = body['actions'][0]['value']
    print(tv_id)
    tv_name = body['actions'][0]['text']['text']
    ombi_body = {
        "theMovieDbId": tv_id, "requestAll": True, "latestSeason": True, "firstSeason": True
        }
    ombi_json = json.dumps(ombi_body)
    try:
        get_url = OMBI_SEARCH_URL + f"/{tv_id}"
        get_req = requests.get(get_url, headers=OMBI_HEADERS)
        get_json = json.loads(get_req.text)
        if get_json['approved'] is True and get_json['available'] is True:
            app.client.chat_postMessage(
                channel=body['user']['id'],
                text=f"{tv_name} is already available!"
            )
        elif get_json['approved'] is True and get_json['available'] is False:
            app.client.chat_postMessage(
                channel=body['user']['id'],
                text=f"{tv_name} is already requested!"
            )
        else:
            requests.post(OMBI_TV_URL, data=ombi_json, headers=OMBI_HEADERS)
            ombi_movie_link = OMBI_BASE_URL + "/details/tv/" + str(tv_id)
            app.client.chat_postMessage(
            channel=body['user']['id'],
            text=f"Requesting <{ombi_movie_link}|{tv_name}>! Feel free to monitor <#CR3C99R7V> for notifications!"
            )
    except HTTPError as err:
        print(err)
    del_body = {"delete_original": "true"}
    body_json = json.dumps(del_body)
    try:
        requests.post(response_url, data=body_json)
    except HTTPError as err:
        print(err)
