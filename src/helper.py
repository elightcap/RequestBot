import os

from dotenv import load_dotenv
from slack_bolt import App

load_dotenv()
app = App(
    token = os.getenv('SLACK_BOT_TOKEN'),
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
)


def helperfunc(ack,body, say):
    ack()
    mBlocks=[{
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
        blocks=mBlocks,
        text="Choose a helper"
    )

