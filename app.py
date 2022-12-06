import os
import re
import requests

from src.notify import send_slack_notification
from urllib.error import HTTPError
from flask import Flask,jsonify,request

OMBI_API_KEY = "something here"

OMBI_HEADERS = {"ApiKey": OMBI_API_KEY, "Content-Type": "application/json"}

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route('/post', methods=["POST"])
def testpost():
    input_json = request.get_json(force=True)
    print(input_json)
    dictToReturn = {'text':input_json['text']}
    print(dictToReturn)
    return jsonify(dictToReturn)

@app.route('/notify', methods=["POST"])
def notify_slack():
    input_json = request.get_json(force=True)
    print(input_json)
    dictToReturn = {'text':input_json['text']}
    print(dictToReturn)
    requestId = input_json['requestId']
    getUrl = "https://ombi.elightcap.com/api/v1/Request/movie/info/{}".format(requestId)
    getRequest = requests.get(getUrl,headers=OMBI_HEADERS)
    alias = getRequest.json()["requestedByAlias"]
    name = getRequest.json()["requestedByAlias"]
    send_slack_notification(alias,name)
    return jsonify(dictToReturn)
