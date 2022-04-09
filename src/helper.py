import os

from dotenv import load_dotenv
from slack_bolt import App

load_dotenv()
app = App(
    token = os.getenv('SLACK_BOT_TOKEN'),
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
)


def helperfunc(ack,body):
    """helper function. sends buttons to user to select help category"""
    ack()
    m_blocks=[{
        "type": "actions",
        "block_id": "helper_actions",
        "elements": [
            {
                "type": "button",
                "action_id": "tv_helper_button",
                "text": {
                    "type": "plain_text",
                    "text": "Tv Helper",
                    "emoji": True
                },
                "value": "tv_helper"
            },
            {
                "type": "button",
                "action_id": "movie_helper_button",
                "text": {
                    "type": "plain_text",
                    "text": "Movie Helper",
                    "emoji": True
                },
                "value": "movie_helper"
            },
            {
                "type": "button",
                "action_id": "invite_helper_button",
                "text": {
                    "type": "plain_text",
                    "text": "Invite Helper",
                    "emoji": True
                },
                "value": "invite_helper"
            }
        ]
    }]
    app.client.chat_postMessage(
        channel=body['user_id'],
        blocks=m_blocks,
        text="Choose a helper"
    )

def helper_button_actions(ack,body):
    """helper buttons function. Sends a message to the user based on the button pressed"""
    ack()
    if body["actions"][0]["value"] == "tv_helper":
        app.client.chat_postMessage(
            channel=body['user']['id'],
            text="""To request a TV show, try the requesttv slash command!
             For example `/requesttv The Flash`."""
        )
    elif body["actions"][0]["value"] == "movie_helper":
        app.client.chat_postMessage(
            channel=body['user']['id'],
            text="""To request a movie, try the requestmovie slash command!
             For example `/requestmovie The Godfather`. """
        )
    elif body["actions"][0]["value"] == "invite_helper":
        app.client.chat_postMessage(
            channel=body['user']['id'],
            text="""To request an invite to a Jellyfin server, try the requestinvite slash command!
             For example `/requestinvite test@example.com`. Your request will be sent to the Jellyfin server admin for approval. 
             You will recieve a message containing username and password 
             if your request is approved."""
        )
