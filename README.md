# RequestBot

## A Slack bot that lets you interact with Ombi to request movies and TV shows

###Requirements

* Python3
* Ombi API Key
* MovieDB API Key
* Slack App setup with Event Subscriptions and Interactive Components

###Installation
* Create a Slack app https://api.slack.com/start
* Clone this repository `git clone https://github.com/elightcap/RequestBot.git`
* copy the env example `cp env.sample .env`
* Change values in .env `nano .env`
* Install requirements `pip install -r requirements.txt`
* Run bot `python3 ./requestbot.py`

###Interacting with the bot
If scoped properly, bot can reply to direct messages or @mentions in channels it has been added to

* `requestmovie the matrix`
* `@requestbot requestmovie the matrix`
* `requesttv The office`
* `@requestbot requesttv the office`

###Limitations
* Currently, I limit what is returned to a total of 4 items.  This is because i am bad at this, and the way I've done things is slow.  If the item you are searching for is missing, try being more specific, ie 'The Matrix Resurrections' instead of just 'The Matrix'.
* Because im bad at this, whenever you click a button, slack will think the request errored out.  Slack requires a response within 3 seconds and my stuff is too slow.  Its not intrusive and doesnt really matter
* This will likely break.  I didnt test a lot.  If it breaks put an issue in, or make a Pull request.
