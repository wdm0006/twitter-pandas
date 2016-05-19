API Usage
=========

The TwitterPandas client is a wrapper around a tweepy connection that allows you to simply interact with the twitter api
and get back pandas dataframes pre-flattened.  You can always also access the underlying tweepy connection to get back
raw responses if you prefer.

Setting up a connection
-----------------------

To set up a connection just:

.. code-block:: python

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



Detailed API Documentation
--------------------------

.. automodule:: twitterpandas.client
   :members: