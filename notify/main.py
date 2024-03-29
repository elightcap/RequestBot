import os
import re
import requests
import json

from src.notify import send_slack_notification
from urllib.error import HTTPError
from flask import Flask,jsonify,request
from dotenv import load_dotenv

load_dotenv()

OMBI_API_KEY = os.getenv('OMBI_API_KEY')
OMBI_HEADERS = {"ApiKey": OMBI_API_KEY, "Content-Type": "application/json"}

JELLYFIN_API_KEY = os.getenv('JELLYFIN_API_KEY')
JELLYFIN_URL = os.getenv('JELLYFIN_URL')
JELLYFIN_HEADERS = {
    "X-Emby-Authorization": "Mediabrowser Token=" + JELLYFIN_API_KEY,
    "Content-Type": "application/json"
    }

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route('/notify', methods=["POST"])
def notify_slack():
    try:
        input_json = request.get_json(force=True)
        print(input_json)
        requestId = input_json['requestId']
        getUrl = "https://ombi.elightcap.com/api/v1/Request/movie/info/{}".format(requestId)
        getRequest = requests.get(getUrl,headers=OMBI_HEADERS)
        getRequestJson = getRequest.json()
        alias = getRequestJson["requestedByAlias"]
        name = getRequestJson["title"]
        print(alias)
        print(name)
        send_slack_notification(alias,name)
        return "200"
    except Exception as e:
        return "500"

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True) 
