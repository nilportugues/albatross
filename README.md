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

    TWITTER_CONSUMER_KEY=<secret>
    TWITTER_CONSUMER_SECRET=<secret>
    ```
  Note that the values aren't wrapped in quotes.  You can thank Docker for
  that.

## Running

Just run `docker-compose up` and wait while it downloads all of the components
and starts up the various containers.  When it's finished, you should be able
to visit http://localhost:8000/ and then login with Twitter to start your
first collection.

