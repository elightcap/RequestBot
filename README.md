# RequestBot

## A Slack bot that lets you interact with Ombi to request movies and TV shows

### Requirements

* Python3
* Ombi API Key
* MovieDB API Key
* Slack App setup with Event Subscriptions and Interactive Components
* Port 3001 from the internet forwarded to the device running the bot or a reverse proxy
* (Optional) Jellyfin

### Installation

* Create a Slack app https://api.slack.com/start
* Clone this repository `git clone https://github.com/elightcap/RequestBot.git`
* copy the env example `cp env.sample .env`
* Change values in .env `nano .env`
* Install requirements `pip install -r requirements.txt`
* Run bot `python3 ./requestbot.py`

### Interacting with the bot

If scoped properly, bot can reply to direct messages or @mentions in channels it has been added to

* `requestmovie the matrix`
* `@requestbot requestmovie the matrix`
* `requesttv The office`
* `@requestbot requesttv the office`
* `/requestmovie the matrix`
* `/requesttv the office`
* `/requestinvite youremail@example.com`
### Limitations

* Currently, I limit what is returned to a total of 4 items.  This is because i am bad at this, and the way I've done things is slow.  If the item you are searching for is missing, try being more specific, ie 'The Matrix Resurrections' instead of just 'The Matrix'.
* ~~Because im bad at this, whenever you click a button, slack will think the request errored out.  Slack requires a response within 3 seconds and my stuff is too slow.  Its not intrusive and doesnt really matter.~~ This should be fixed now.
* This will likely break.  I didnt test a lot.  If it breaks put an issue in, or make a Pull request.
* The invite command only works with Jellyfin.  I can't find good documentation for plex so ¯\\\_(ツ)_/¯

### ToDo

* Optimization
* More commands (mostly around getting the current queue)
* ~~Maybe make a slash command?~~ This is added
