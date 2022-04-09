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
TV_URL = "https://api.themoviedb.org/4/search/tv?query="

def tv_req(ack,body):
    ack()
    try:
        text = body['text']
        tvUrlEncode = urllib.parse.quote(text)
        dbReqUrl = TV_URL + tvUrlEncode
        dbReq = requests.get(dbReqUrl, headers=MOVIE_DB_HEADERS)
        dbReqJson = json.loads(dbReq.text)
        print(dbReqJson)
        if(len(dbReqJson['results']) > 1):
            count = len(dbReqJson['results'])
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
    except KeyError as e:
        app.client.chat_postMessage(
            channel=body['user_id'],
            text="Please enter a tv show name with your request"
        )
        return

