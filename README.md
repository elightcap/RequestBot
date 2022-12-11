# RequestBot

## A Slack bot that lets you interact with Ombi to request movies and TV shows

### Requirements

* [Slack](https://slack.com/)
* [Ombi](https://ombi.io)
* [Ombi API](https://ombi.io/api)
* [MovieDB API Key](https://www.themoviedb.org/settings/api)
* Slack App setup with Event Subscriptions and Interactive Components
* Port 3001 from the internet forwarded to the device running the bot or a reverse proxy
* (Optional) [Jellyfin](https://jellyfin.org)
* (Optional) [Jellyfin API Key](https://jellyfin.org/docs/api/authentication)
* (Optional) [Docker](https://docs.docker.com/get-docker/)

### Installation

#### Docker

Docker is the recommended method of installation

* [Create a Slack app](https://api.slack.com/start)
* Clone this repository `git clone https://github.com/elightcap/RequestBot.git`
* Add the required values to the sample.env file `cd Requestbot && nano sample.env`
* Run the following to put the .env in the right places: `cp sample.env ./notify/.env && cp sample.env ./slackbot/.env`
* Build the images `docker compose build`
* Start the containers `docker compose up -d`

#### Run with Python

If you dont want to use docker, the bots can be run natively with python3. Recommend a terminal multiplexer like [tmux](https://github.com/tmux/tmux/wiki)

* [Create a Slack app](https://api.slack.com/start)
* Clone this repository `git clone https://github.com/elightcap/RequestBot.git`
* Add the required values to the sample.env file `cd Requestbot && nano sample.env`
* Run the following to put the .env in the right places: `cp sample.env ./notify/.env && cp sample.env ./slackbot/.env`
* Install requirements `cd ./notify && pip install -r requirements.txt`
* Run bots `python3 ./slackbot/main.py` `python3 ./notify/main.py` (this is where tmux comes in handy)

### Interacting with the bot

If scoped properly, bot can reply to direct messages or @mentions in channels it has been added to

* `/help` - Displays help message
* `/requestmovie the matrix` - Requests a movie when typing `/requestmovie` in a channel the bot is added to
* `/requesttv the office` - Requests a TV show when typing `/requesttv` in a channel the bot is added to
* `/requestinvite youremail@example.com` - Requests an invite to Jellyfin
### Limitations

* ~Currently, I limit what is returned to a total of 4 items.  This is because i am bad at this, and the way I've done things is slow.  If the item you are searching for is missing, try being more specific, ie 'The Matrix Resurrections' instead of just 'The Matrix'.~ This isnt the case anymore, were returning a full list of results.
* ~~Because im bad at this, whenever you click a button, slack will think the request errored out.  Slack requires a response within 3 seconds and my stuff is too slow.  Its not intrusive and doesnt really matter.~~ This should be fixed now.
* This will likely break.  I didnt test a lot.  If it breaks put an issue in, or make a Pull request.
* The invite command only works with Jellyfin.  I can't find good documentation for plex so ¯\\\_(ツ)_/¯

### ToDo

* Add support for Plex (not sure this is possible)
* Optimization
* More commands (mostly around getting the current queue)
* ~~Maybe make a slash command?~~ This is added
* Kinda want to add @ mentions back, so the bot can be mentioned from a channel and maybe people can vote on the request?
* Think about forking to discord.  Its pretty much a full rewrite, but it would be nice to have a discord bot that can do the same things.
