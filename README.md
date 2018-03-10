# Albatross

A Twitter live-data collector.  Keep an eye on your disk space ;-)


## Setup

Everything is dockerised, so you need:

* Docker
* Docker Compose
* A `.env` file defining the following values:
    ```
    PYTHONUNBUFFERED=1

    SECRET_KEY=<secret>
    DEBUG=true
    ADMINS=[["Your Name", "your@email.address"]]
    VERBOSITY=3

    TWITTER_CONSUMER_KEY=<secret>
    TWITTER_CONSUMER_SECRET=<secret>
    ```
  Note that the values aren't wrapped in quotes.  You can thank Docker for
  that.


## Running

It's currently two steps: building the container and running the composer:

1. `docker build . -t danielquinn/albatross`
2. `docker-compose up`

When it's finished, you should be able to visit http://localhost:8000/ and then
login with Twitter to start your first collection.


## Architecture

Here's what it's doing under the hood:

![Architecture](docs/architecture.png)


## TODO

### Backfilling

Currently, we're only collecting tweets that come *after* the collector is
started, which isn't ideal if you start the collector after a key event.  To
backfill tweets however I'm going to have to experiment with the API limits
on the REST search query:

```python
import tweepy
socialtoken = SocialToken.objects.first()
socialapp = SocialApp.objects.get(pk=1)
auth = tweepy.OAuthHandler(socialapp.client_id, socialapp.secret)
auth.set_access_token(socialtoken.token, socialtoken.token_secret)

for tweet in tweepy.Cursor(tweepy.API(auth).search, "fuck").items(10):
    print(f"{tweet.created_at}: {tweet.text}")
```


### Distilling

Currently, all tweets are stored in separate `.fjson.xz` files, broken up into
segments so we don't carry too much in memory.  We need a management command
that will combine all of these files into one.
