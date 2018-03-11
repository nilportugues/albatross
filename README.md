# Albatross

A Twitter live-data collector.  Keep an eye on your disk space ;-)


## What is This?

This project is largely an experiment that may one day grow into something
useful for more than just a handful of people.

> The idea is simple: Albatross is a way for you to capture everything said
> about something and then analyse the raw data yourself or let this site
> visualise it for you.

Say you're at a conference that's managing the conversation with the hashtag:
`#awesomeconference`.  You're participating when you can, but it would be
really nice to be able to collect everything everyone said during the
conference and draw some conclusions from it.

Maybe you want to do some analytics based on some natural language processing,
or want to chart the number of times a particular phrase was mentioned within
that hashtag.  Whatever you want to do with the data, just fill out the form
here with the hashtag in question, hit `submit` and when the conference ends,
you've got all the data to play with.

Similarly this can be used for international events, or national disaster
coverage.  Plot on a map the tweets posted about your subject and when, or
analyse the content of the tweets to see what different regions are saying
about a particular subject.


## Can You Do That For Me?

Analytics and visualisation is hard, and not everyone has the time or
inclination to figure out how to parse the JSON blobs Twitter makes available
via their API.  Thankfully, Albatross has a bunch of built-in visualisations
that might be sufficient for many people, but if you need something more
customised, you can open an issue and I can give it a shot.  Of course,
contributions are welcome!


## Data Format

The raw data is available as a xzip-compressed "fjson" file.  This is just a
plain text file, with one JSON object per line.  You can decompress this file
in Linux & Mac with the <code>xz</code> utility, or use a common program like
WinRar in Windows.


## Setup

Everything is dockerised, so you need:

* Docker
* Docker Compose
* A `.env` file defining the following values:
    ```
    PYTHONUNBUFFERED=1

    SECRET_KEY=<secret>
    DEBUG=false
    ADMINS=[["Your Name", "your@email.address"]]
    DJANGO_LOG_LEVEL="INFO"

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
