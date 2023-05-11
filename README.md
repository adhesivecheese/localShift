# localShift

localShift is intended to be a self-hosted, single subreddit archiving tool to help fill the gap the demise of pushshift has left in many moderators ability to moderate effectively.

## Installation
To install:
* download the source, fill out the first two lines in [constants.py](/constants.py)
  * `PRAW_USER` should be the name of a site in your `praw.ini` file, for a script type app. See [here]([https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html](https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html#defining-additional-sites)) if you're unfamiliar with this method of defining a bot.
  * `SUBREDDIT` should be the name of the subreddit you wish to monitor. *Just* the name, no preceding `/r/`
* run with `python localshift.py` (or `python3 localshift.py`)

The API may be run seperately by running the command `python -m uvicorn api:app` (or `python3 -m uvicorn api:app`)

## About the API
The API is incredibly rudamentary at this point, with only two functional endpoints:
* `/api/v0/post/{id}` for posts
* `/api/v0/comment/{id}` for comments
* 
where `{id}` is the id of the post or comment you wish to fetch.

## Future Plans
In addition to expanding the API, full-text search and a graphical front-end are planned features of localShift. Pull requests and bug reports are welcome.
