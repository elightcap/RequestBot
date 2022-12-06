import os
import re

from urllib.error import HTTPError
from flask import Flask,jsonify,request
import requests

app = Flask(__name__)


@app.route('/post', methods=["POST"])
def testpost():
    input_json = request.get_json(force=True) 
    dictToReturn = {'text':input_json['text']}
    print(dictToReturn)
    return jsonify(dictToReturn)
