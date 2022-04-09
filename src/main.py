import os
import re

from helper import helperfunc

from slack_bolt import App
from dotenv import load_dotenv


load_dotenv()
app = App(
    token = os.getenv('SLACK_BOT_TOKEN'),
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
)
#CHAT = app.client.chat_postMessage()

@app.command("/requestmovie")
def help(ack,body,logger):
    helperfunc(ack,body)

@app.action(re.compile("helper_button$"))
def handle_some_action(ack, body, logger):
    ack()
    print(body)


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3001)))