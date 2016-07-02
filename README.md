twitter-pandas
==============

version number: 0.0.1
author: Will McGinnis

Overview
--------

A library for getting and interacting with twitter data via pandas.  Currently very in-flux, based heavily on my other
library of this type: [git-pandas](https://github.com/wdm0006/git-pandas).

### Current State

The library itself is based heavily on [tweepy](http://docs.tweepy.org/en/v3.5.0/), and as such the development and API 
to twitter-pandas will follow it's API pretty closely.  To start with I've implemented the:

 * user methods
 * timeline methods
 * favorite methods
 * account methods
 * trends methods
 * list methods
 * saved search methods
 * status methods
 * direct message methods
 * friendship methods
  
As well as some helper properties:

 * api_id
 * api_screen_name
 
Which help access data tied to the API key's account quickly.

### Roadmap

Going forward, we will work our way through [tweepy's api](http://docs.tweepy.org/en/v3.5.0/api.html), providing 
pandas-based interfaces to the methods in each of these groupings that return datasets (for now we are trying to stay 
read-only where practical, with a data analysis focus).

 * block methods
 * help methods
 * geo methods
 
The general idea is to:

 * Use sensible defaults to make interfaces sensible, intuitive, and safe
 * Provide raw datasets as pandas dataframes for all common api endpoints that return data
 * Provide some processed datasets for common analysis tasks:
    * people who I follow who don't follow me (and vice versa)
    * top users of a hashtag
    * top followers of mine
    * follower growth charts
    * etc.
    
Any feedback on analysis tasks that you commonly do and could be made simpler with this library would be extremely 
valuable, so please open up an issue with suggestions.
 
Installation / Usage
--------------------

To install use pip:

    $ pip install git+https://github.com/wdm0006/twitter-pandas.git


Or clone the repo:

    $ git clone https://github.com/wdm0006/twitter-pandas.git
    $ python setup.py install
    
Then let 'er rip:

    from twitterpandas import TwitterPandas
    
    # create a twitter pandas client object
    tp = TwitterPandas(
        TWITTER_OAUTH_TOKEN,
        TWITTER_OAUTH_SECRET,
        TWITTER_CONSUMER_KEY,
        TWITTER_CONSUMER_SECRET
    )
    
    # create a dataframe with 10 of my own followers
    df = tp.followers(limit=10)
    print(df.head())
    
    # create a dataframe with my own information
    df = tp.me()
    print(df)
    
    # get a dataframe with the information of user willmcginnis
    df = tp.get_user(screen_name='willmcginnis')
    print(df)
    
    # get back 10 users who match the query willmcginnis
    df = tp.search_users(query='willmcginnis', limit=10)
    print(df)
    
Contributing
------------

We are looking for contributors, so if you are interested, please review our contributor guidelines in CONTRIBUTING.md,
which includes some proposed starter issues, or if you have an idea of your own, send us a pull request.

Examples
--------

There are some examples in the examples directory, to run them, you need API credentials.  Add a keys.py file (and make
sure it's gitignored) with the format:

    TWITTER_OAUTH_TOKEN = 'foo'
    TWITTER_OAUTH_SECRET = 'bar'
    TWITTER_CONSUMER_KEY = 'baz'
    TWITTER_CONSUMER_SECRET = 'bat'
    
And the examples should work for you. If you run into any issues, feel free to open an issue and I'll try to help you out.