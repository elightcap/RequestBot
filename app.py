import os
import re

from urllib.error import HTTPError
from flask import Flask,jsonify,request
import requests

app = Flask(__name__)


@app.route('/notify')
def hello_world():
    print("call")
    return 'This is my first API call!'
