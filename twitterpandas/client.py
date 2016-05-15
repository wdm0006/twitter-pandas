"""
.. module::
   :platform: Unix, Windows
   :synopsis:

.. moduleauthor:: Will McGinnis <will@pedalwrencher.com>


"""

import warnings
import tweepy
import pandas as pd

__author__ = 'willmcginnis'


class TwitterPandas(object):
    """
    The primary interface into twitter pandas, the client.

    """

    def __init__(self, oauth_token, oauth_secret, consumer_key, consumer_secret, timeout=60):
        """
        Basic interface to twitter pandas is pretty much a wrapper around tweepy.  As such, we take in very similar args
        to the main constructor.

        :param oauth_token:
        :param oauth_secret:
        :param consumer_key:
        :param consumer_secret:
        :param timeout:
        :return:

        """

        # configure OAUTH
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(oauth_token, oauth_secret)

        # set up tweepy client
        self.client = tweepy.API(
            auth,
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True,
            timeout=True
        )

    # #################################################################
    # #####  Internal functions and protected methods             #####
    # #################################################################
    def _flatten_dict(self, data, layers=1, drop_deeper=True):
        """
        takes in a dictionary and will flatten it with level_1.level_2 as the key, for however many levels are
        specified. If specified (true by default), anything deeper than the specified level will be dropped from the
        dictionary outright.

        :param data:
        :param layers:
        :param drop_deeper:
        :return:
        """

        for _ in range(layers):
            data = [(k, v) if not isinstance(v, dict) else [(k + '.' + k2, v2) for k2, v2 in v.items()] for k, v in data.items()]
            data = [item for sublist in data for item in sublist if isinstance(sublist, list)] + [y for y in data if not isinstance(y, list)]
            data = dict(data)

        if drop_deeper:
            data = {k: v for k, v in data.items() if not isinstance(v, dict) or isinstance(v, list)}

        return data

    def __str__(self):
        """

        :return:
        """

        return 'TwitterPandas Client For u=%s' % (self._api_username())

    def _api_screen_name(self):
        """
        Returns the API screen name

        :return:
        """
        return self.me()['screen_name'].values[0]

    def _api_id(self):
        """

        :return:
        """
        return self.me()['id'].values[0]

    @property
    def api_screen_name(self):
        return self._api_screen_name()

    @property
    def api_id(self):
        return self._api_id()

    # #################################################################
    # #####  User Methods                                         #####
    # #################################################################
    def followers(self, id_=None, user_id=None, screen_name=None, limit=None):
        """
        Returns a dataframe of all data about followers for the user tied to the API keys.

        :param limit:
        :return:
        """

        # create a tweepy cursor to safely return the data
        curr = tweepy.Cursor(
            self.client.followers,
            id_=id_,
            user_id=user_id,
            screen_name=screen_name
        )

        # page through it and parse results
        ds = []
        for follower in curr.items():
            # get the raw json, flatten it one layer and then discard anything nested farther
            ds.append(self._flatten_dict(follower._json, layers=3, drop_deeper=True))

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    def search_users(self, query=None, limit=None):
        """
        Lets you structure a query and returns a dataframe with all of the users that match that query (max 1000 results
        as per API rules)

        :param query:
        :param limit:
        :return:
        """

        if limit > 1000:
            warnings.warn('WARNING: twitter\'s API will only return 1000 results, so we do too. Your limit isn\'t really doing anything here')

        # create a tweepy cursor to safely return the data
        curr = tweepy.Cursor(
            self.client.search_users,
            q=query
        )

        # page through it and parse results
        ds = []
        for user in curr.items():
            # get the raw json, flatten it one layer and then discard anything nested farther
            ds.append(self._flatten_dict(user._json, layers=3, drop_deeper=True))

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    def get_user(self, id_=None, user_id=None, screen_name=None,):
        """
        Returns a dataframe with just one row, which contains all the information we have about that specific user.

        :param id:
        :param user_id:
        :param screen_name:
        :return:
        """

        data = self.client.get_user(
            id_=id_,
            user_id=user_id,
            screen_name=screen_name
        )

        # page through it and parse results
        ds = [self._flatten_dict(data._json, layers=3, drop_deeper=True)]

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    def me(self):
        """
        Returns a dataframe with just one row, which has all of the data avilable about the user tied to the API key.

        :return:
        """

        data = self.client.me()

        # page through it and parse results
        ds = [self._flatten_dict(data._json, layers=3, drop_deeper=True)]

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    # #################################################################
    # #####  Timeline Methods                                     #####
    # #################################################################
    def home_timeline(self, since_id=None, max_id=None, limit=None):
        """

        :param since_id:
        :param max_id:
        :param limit:
        :return:
        """

        # create a tweepy cursor to safely return the data
        curr = tweepy.Cursor(
            self.client.home_timeline,
            since_id=since_id,
            max_id=max_id,
            count=limit
        )

        # page through it and parse results
        ds = []
        for status in curr.items():
            # get the raw json, flatten it one layer and then discard anything nested farther
            ds.append(self._flatten_dict(status._json, layers=3, drop_deeper=True))

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    def statuses_lookup(self, id_=None, include_entities=None, trim_user=None, limit=None):
        """

        :param id:
        :param include_entities:
        :param trim_user:
        :return:
        """

        # create a tweepy cursor to safely return the data
        data = self.client.statuses_lookup(
            id_=id_,
            include_entities=include_entities,
            trim_user=trim_user
        )

        # page through it and parse results
        ds = [self._flatten_dict(x._json, layers=3, drop_deeper=True) for x in data]

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    def user_timeline(self, id_=None, user_id=None, screen_name=None, since_id=None, max_id=None, limit=None):
        """

        :param id:
        :param user_id:
        :param screen_name:
        :param since_id:
        :param max_id:
        :param limit:
        :return:
        """

        # create a tweepy cursor to safely return the data
        curr = tweepy.Cursor(
            self.client.user_timeline,
            id_=id_,
            user_id=user_id,
            screen_name=screen_name,
            since_id=since_id,
            max_id=max_id,
            count=limit
        )

        # page through it and parse results
        ds = []
        for status in curr.items():
            # get the raw json, flatten it one layer and then discard anything nested farther
            ds.append(self._flatten_dict(status._json, layers=3, drop_deeper=True))

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    def retweets_of_me(self, since_id=None, max_id=None, limit=None):
        """

        :param since_id:
        :param max_id:
        :param limit:
        :return:
        """

        # create a tweepy cursor to safely return the data
        curr = tweepy.Cursor(
            self.client.retweets_of_me,
            since_id=since_id,
            max_id=max_id,
            count=limit
        )

        # page through it and parse results
        ds = []
        for status in curr.items():
            # get the raw json, flatten it one layer and then discard anything nested farther
            ds.append(self._flatten_dict(status._json, layers=3, drop_deeper=True))

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df