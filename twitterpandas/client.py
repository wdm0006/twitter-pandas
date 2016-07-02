"""
.. module::
   :platform: Unix, Windows
   :synopsis:

.. moduleauthor:: Will McGinnis <will@pedalwrencher.com>


"""

import warnings
import sys

import tweepy
import pandas as pd

__author__ = 'willmcginnis'

NON_BMP_MAP = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)


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
            data = [(k, v) if not isinstance(v, dict) else [(k + '.' + k2, v2) for k2, v2 in v.items()] for k, v in
                    data.items()]
            data = [item for sublist in data for item in sublist if isinstance(sublist, list)] + [y for y in data if
                                                                                                  not isinstance(y,
                                                                                                                 list)]
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

    @property
    def credentials_valid(self):
        return self.client.verify_credentials() is not False

    # #################################################################
    # #####  Account Methods                                      #####
    # #################################################################
    def rate_limit_status(self):
        """
        Returns a dataframe with the rate limit status for all resources and endpoints in the API.

        :return:
        """

        data = self.client.rate_limit_status()

        ds = []
        for resource in data.get('resources', {}).keys():
            for endpoint in data.get('resources').get(resource).keys():
                ds.append({
                    'resource': resource,
                    'endpoint': endpoint,
                    'reset': data.get('resources').get(resource).get(endpoint).get('reset'),
                    'limit': data.get('resources').get(resource).get(endpoint).get('limit'),
                    'remaining': data.get('resources').get(resource).get(endpoint).get('remaining'),
                })

        df = pd.DataFrame(ds)

        df['reset'] = pd.to_datetime(df['reset'], unit='s')

        return df

    # #################################################################
    # #####  Trends Methods                                       #####
    # #################################################################
    def trends_available(self):
        """

        :return:
        """

        data = self.client.trends_available()

        ds = []
        for trend in data:
            ds.append(self._flatten_dict(trend, layers=3, drop_deeper=True))

        df = pd.DataFrame(ds)

        return df

    def trends_place(self, id_=None, exclude=None):
        """
        Returns the trending topics for a given location id (can find it with the trends closest function).

        :param id_:  The Yahoo! Where On Earth ID of the location to return trending information for. Global information is available by using 1 as the WOEID.
        :param exclude: Setting this equal to hashtags will remove all hashtags from the trends list.
        :return:
        """

        data = self.client.trends_place(id=id_, exclude=exclude)

        ds = []
        for trend in data:
            as_of = trend.get('as_of')
            created_at = trend.get('created_at')
            woeid = trend.get('locations', [{}])[0].get('woeid')
            name = trend.get('locations', [{}])[0].get('name')
            for trend_topic in trend.get('trends', []):
                ds.append({
                    'as_of': as_of,
                    'created_at': created_at,
                    'woeid': woeid,
                    'location_name': name,
                    'name': trend_topic.get('name'),
                    'promoted_content': trend_topic.get('name'),
                    'query': trend_topic.get('query'),
                    'tweet_volume': trend_topic.get('tweet_volume'),
                    'url': trend_topic.get('url')
                })

        df = pd.DataFrame(ds)

        return df

    def trends_closest(self, lat=None, long=None):
        """
        Returns a one row dataframe with the woeid and location information closes to the coordinates passed.

        :param lat: If provided with a long parameter the available trend locations will be sorted by distance, nearest to furthest, to the co-ordinate pair. The valid ranges for longitude is -180.0 to +180.0 (West is negative, East is positive) inclusive.
        :param long: If provided with a lat parameter the available trend locations will be sorted by distance, nearest to furthest, to the co-ordinate pair. The valid ranges for longitude is -180.0 to +180.0 (West is negative, East is positive) inclusive.
        :return:
        """

        data = self.client.trends_closest(lat=lat, long=long)

        ds = []
        for trend in data:
            ds.append(self._flatten_dict(trend, layers=3, drop_deeper=True))

        df = pd.DataFrame(ds)

        return df

    # #################################################################
    # #####  User Methods                                         #####
    # #################################################################
    def followers(self, id_=None, user_id=None, screen_name=None, limit=None):
        """
        Returns a dataframe of all data about followers for the user tied to the API keys.

        :param id_: Specifies the ID or screen name of the user.
        :param user_id: Specifies the ID of the user. Helpful for disambiguating when a valid user ID is also a valid screen name.
        :param screen_name: Specifies the screen name of the user. Helpful for disambiguating when a valid screen name is also a user ID.
        :param limit: the maximum number of rows to return (optional, default None for all rows)
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

        :param query: The query to run against people search.
        :param limit: the maximum number of rows to return (optional, default None for all rows)
        :return:
        """

        if limit > 1000:
            warnings.warn(
                'WARNING: twitter\'s API will only return 1000 results, so we do too. Your limit isn\'t really doing anything here')

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

    def get_user(self, id_=None, user_id=None, screen_name=None, ):
        """
        Returns a dataframe with just one row, which contains all the information we have about that specific user.

        :param id_: Specifies the ID or screen name of the user.
        :param user_id:  Specifies the ID of the user. Helpful for disambiguating when a valid user ID is also a valid screen name.
        :param screen_name: Specifies the screen name of the user. Helpful for disambiguating when a valid screen name is also a user ID.
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

        :param since_id: Returns only statuses with an ID greater than (that is, more recent than) the specified ID.
        :param max_id: Returns only statuses with an ID less than (that is, older than) or equal to the specified ID.
        :param limit: the maximum number of rows to return (optional, default None for all rows)
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

        :param id_: A list of Tweet IDs to lookup, up to 100
        :param include_entities: A boolean indicating whether or not to include [entities](https://dev.twitter.com/docs/entities) in the returned tweets. Defaults to False.
        :param trim_user: A boolean indicating if user IDs should be provided, instead of full user information. Defaults to False.
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

        :param id_: Specifies the ID or screen name of the user.
        :param user_id: Specifies the ID of the user. Helpful for disambiguating when a valid user ID is also a valid screen name.
        :param screen_name: Specifies the screen name of the user. Helpful for disambiguating when a valid screen name is also a user ID.
        :param since_id: Returns only statuses with an ID greater than (that is, more recent than) the specified ID.
        :param max_id: Returns only statuses with an ID less than (that is, older than) or equal to the specified ID.
        :param limit: the maximum number of rows to return (optional, default None for all rows)
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

        :param since_id: Returns only statuses with an ID greater than (that is, more recent than) the specified ID.
        :param max_id: Returns only statuses with an ID less than (that is, older than) or equal to the specified ID.
        :param limit: the maximum number of rows to return (optional, default None for all rows)
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

    # #################################################################
    # #####  Favorite Methods                                     #####
    # #################################################################
    def favorites(self, id_=None, limit=None):
        """
        Returns a dataframe of all data about followers for the user tied to the API keys.

        :param id_: Specifies the ID or screen name of the user.
        :param limit: the maximum number of rows to return (optional, default None for all rows)
        :return:
        """

        # create a tweepy cursor to safely return the data
        curr = tweepy.Cursor(
            self.client.favorites,
            id_=id_,
        )

        # page through it and parse results
        ds = []
        for favorite in curr.items():
            # get the raw json, flatten it one layer and then discard anything nested farther
            ds.append(self._flatten_dict(favorite._json, layers=3, drop_deeper=True))

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    # #################################################################
    # #####  Saved Searches Methods                               #####
    # #################################################################
    def saved_searches(self):
        """
        Returns saved search attributes for the user tied to the API keys,
        as a Pandas DataFrame that contains created_at, id, id_str, 
        name, position, query as columns

        :return:
        """

        data = self.client.saved_searches()

        ds = []

        # loop through SavedSearch objects return from the API
        for saved_search in data:
            # remove _api attribute
            saved_search.__dict__.pop('_api')
            # flatten the dictionary attribute of the object
            ds.append(self._flatten_dict(saved_search.__dict__, layers=3))

        # convert the flattened dictionaries to a dataframe
        df = pd.DataFrame(ds)

        return df

    def get_saved_search(self, id_):
        """
        Returns saved search attributes for one specific saved search object as a Pandas DataFrame
        that contains created_at, id, id_str, name, position, query as columns

        :param id_: Specifies the ID of the saved search object to convert to a DataFrame
        :return:
        """

        # get saved search from the API
        data = self.client.get_saved_search(id_)

        ds = []

        # remove _api attribute
        data.__dict__.pop('_api')

        # append single saved search
        ds.append(self._flatten_dict(data.__dict__))

        # convert a single SavedSearch object to a dataframe
        df = pd.DataFrame(ds)

        return df

    # #################################################################
    # #####  Direct Message Methods                               #####
    # #################################################################
    def direct_messages(self, since_id=None, max_id=None, limit=1, page=1, full_text=False, include_user_data=False):
        """
        Returns direct messages sent to the user tied to the API keys, in the form
        of a Pandas DataFrame

        :param since_id:
        :param max_id:
        :param count:
        :param page:
        :param full_text:
        :return:
        """

        # get direct messages sent to the user from the API
        data = self.client.direct_messages(since_id=since_id, max_id=max_id,
                                           count=limit, page=page, full_text=full_text)

        ds = []
        for direct_message in data:
            dict_data = self._flatten_dict(direct_message.__dict__)

            temp_data_dict = {}

            temp_data_dict['created_at'] = dict_data['created_at']
            temp_data_dict['id'] = dict_data['id']
            temp_data_dict['id_str'] = dict_data['id_str']

            if dict_data['entities.urls']:
                # only pull one type of URL from entities.url to avoid
                # multiple, repetitive data per row in the entities.url column
                for dictionary in dict_data['entities.urls']:
                    temp_data_dict['entities.urls_url'] = dictionary['url']

            if dict_data['entities.user_mentions']:
                for dictionary in dict_data['entities.user_mentions']:
                    temp_data_dict['entities.user_mentions_id_str'] = dictionary['id_str']
                    temp_data_dict['entities.user_mentions_name'] = dictionary['name']
                    temp_data_dict['entities.user_mentions_screen_name'] = dictionary['screen_name']

            if dict_data['entities.hashtags']:
                for dictionary in dict_data['entities.hashtags']:
                    temp_data_dict['entities.hashtags_text'] = dictionary['text']

            # includes a large amount of data so this uses
            # a user-settable boolean to add in recipient and sender info
            if include_user_data:
                sender_data = self._flatten_dict(dict_data['sender']._json)
                recipient_data = self._flatten_dict(dict_data['recipient']._json)

                for key in sender_data:
                    if "sender_" not in key:
                        sender_data["sender_{}".format(key)] = sender_data.pop(key)

                for key in recipient_data:
                    if "recipient_" not in key:
                        recipient_data["recipient_{}".format(key)] = recipient_data.pop(key)

                merged_data = sender_data.copy()
                merged_data.update(recipient_data)

                # uses translation table to map everything outside of the bmp
                temp_data_dict['full_text'] = dict_data['text'].translate(NON_BMP_MAP)

                merged_data.update(temp_data_dict)

                ds.append(merged_data)

        df = pd.DataFrame(ds)
        return df

    def get_direct_message(self, id_=None, include_user_data=False):
        """
        Returns a single direct message object sent to the user tied to the API keys
        in the form of a Pandas DataFrame

        :param since_id:
        :param id_:
        :param full_text:
        :return:
        """

        # get direct messages sent to the user from the API
        data = self.client.get_direct_message(id=id_)

        ds = []
        dict_data = self._flatten_dict(data.__dict__)

        temp_data_dict = {}

        temp_data_dict['created_at'] = dict_data['created_at']
        temp_data_dict['id'] = dict_data['id']
        temp_data_dict['id_str'] = dict_data['id_str']

        if dict_data['entities.urls']:
            # only pull one type of URL from entities.url to avoid
            # multiple, repetitive data per row in the entities.url column
            for dictionary in dict_data['entities.urls']:
                temp_data_dict['entities.urls_url'] = dictionary['url']

        if dict_data['entities.user_mentions']:
            for dictionary in dict_data['entities.user_mentions']:
                temp_data_dict['entities.user_mentions_id_str'] = dictionary['id_str']
                temp_data_dict['entities.user_mentions_name'] = dictionary['name']
                temp_data_dict['entities.user_mentions_screen_name'] = dictionary['screen_name']

        if dict_data['entities.hashtags']:
            for dictionary in dict_data['entities.hashtags']:
                temp_data_dict['entities.hashtags_text'] = dictionary['text']

        # includes a large amount of data so this uses
        # a user-settable boolean to add in recipient and sender info
        if include_user_data:
            sender_data = self._flatten_dict(dict_data['sender']._json)
            recipient_data = self._flatten_dict(dict_data['recipient']._json)

            for key in sender_data:
                if "sender_" not in key:
                    sender_data["sender_{}".format(key)] = sender_data.pop(key)

            for key in recipient_data:
                if "recipient_" not in key:
                    recipient_data["recipient_{}".format(key)] = recipient_data.pop(key)

            merged_data = sender_data.copy()
            merged_data.update(recipient_data)

            # uses translation table to map everything outside of the bmp
            temp_data_dict['full_text'] = dict_data['text'].translate(NON_BMP_MAP)

            merged_data.update(temp_data_dict)

            ds.append(merged_data)

        df = pd.DataFrame(ds)
        return df

    def sent_direct_messages(self, since_id=None, max_id=None, limit=1, page=1, full_text=False,
                             include_user_data=False):
        """
        Returns direct message objects sent by the user tied to the API keys
        in the form of a Pandas DataFrame

        :param since_id:
        :param max_id:
        :param count:
        :param page:
        :param full_text:
        :return:
        """

        # get direct messages sent by the user from the API
        data = self.client.sent_direct_messages(since_id=since_id, max_id=max_id,
                                                count=limit, page=page, full_text=full_text)

        ds = []
        for direct_message in data:
            dict_data = self._flatten_dict(direct_message.__dict__)

            temp_data_dict = {}

            temp_data_dict['created_at'] = dict_data['created_at']
            temp_data_dict['id'] = dict_data['id']
            temp_data_dict['id_str'] = dict_data['id_str']

            if dict_data['entities.urls']:
                # only pull one type of URL from entities.url to avoid
                # multiple, repetitive data per row in the entities.url column
                for dictionary in dict_data['entities.urls']:
                    temp_data_dict['entities.urls_url'] = dictionary['url']

            if dict_data['entities.user_mentions']:
                for dictionary in dict_data['entities.user_mentions']:
                    temp_data_dict['entities.user_mentions_id_str'] = dictionary['id_str']
                    temp_data_dict['entities.user_mentions_name'] = dictionary['name']
                    temp_data_dict['entities.user_mentions_screen_name'] = dictionary['screen_name']

            if dict_data['entities.hashtags']:
                for dictionary in dict_data['entities.hashtags']:
                    temp_data_dict['entities.hashtags_text'] = dictionary['text']

            # includes a large amount of data so this uses
            # a user-settable boolean to add in recipient and sender info
            if include_user_data:
                sender_data = self._flatten_dict(dict_data['sender']._json)
                recipient_data = self._flatten_dict(dict_data['recipient']._json)

                for key in sender_data:
                    if "sender_" not in key:
                        sender_data["sender_{}".format(key)] = sender_data.pop(key)

                for key in recipient_data:
                    if "recipient_" not in key:
                        recipient_data["recipient_{}".format(key)] = recipient_data.pop(key)

                merged_data = sender_data.copy()
                merged_data.update(recipient_data)

                # uses translation table to map everything outside of the bmp
                temp_data_dict['full_text'] = dict_data['text'].translate(NON_BMP_MAP)

                merged_data.update(temp_data_dict)

                ds.append(merged_data)

        df = pd.DataFrame(ds)
        return df

    # #################################################################
    # #####  Friendship Methods                                   #####
    # #################################################################
    def exists_friendship(self, source_id=None, source_user_id=None, source_screen_name=None, target_id=None,
                          target_user_id=None, target_screen_name=None):
        """
        Checks if a friendship exists between two users. Will return True if user_a follows user_b, otherwise False.

        :param source_id: Specifies the ID or screen name of the source user.
        :param source_user_id: Specifies the ID of the source user. Helpful for disambiguating when a valid user ID is also a valid screen name.
        :param source_screen_name: Specifies the screen name of the source user. Helpful for disambiguating when a valid screen name is also a user ID.
        :param target_id: Specifies the ID or screen name of the target user.
        :param target_user_id: Specifies the ID of the target user. Helpful for disambiguating when a valid user ID is also a valid screen name.
        :param target_screen_name: Specifies the screen name of the target user. Helpful for disambiguating when a valid screen name is also a user ID.
        :return:
        """

        # get friendship from the API
        data = self.client.show_friendship(
            source_id=source_id,
            source_screen_name=source_screen_name,
            target_id=target_id,
            target_screen_name=target_screen_name
        )

        # return value of following attribute for user_a
        return data[0].following

    def show_friendship(self, source_id=None, source_screen_name=None, target_id=None, target_screen_name=None):
        """
        Returns detailed information about the relationship between two users.

        :param source_id: The user_id of the subject user.
        :param source_screen_name: The screen_name of the subject user.
        :param target_id: The user_id of the target user.
        :param target_screen_name: The screen_name of the target user.
        :return:
        """

        # get friendship from the API
        data = self.client.show_friendship(
            source_id=source_id,
            source_screen_name=source_screen_name,
            target_id=target_id,
            target_screen_name=target_screen_name
        )

        ds = []

        # remove _api attribute
        for user in data:
            user.__dict__.pop('_api')

            # append friendship search
            ds.append(self._flatten_dict(user.__dict__))

        # convert a single Friendship objects to a dataframe
        df = pd.DataFrame(ds)

        return df

    def friends_ids(self, id_=None, screen_name=None, user_id=None, limit=None):
        """
        Returns an array containing the IDs of users being followed by the specified user.

        :param id_: Specifies the ID or screen name of the user.
        :param user_id: Specifies the ID of the user. Helpful for disambiguating when a valid user ID is also a valid screen name.1
        :param screen_name: Specifies the screen name of the user. Helpful for disambiguating when a valid screen name is also a user ID.
        :param limit: the maximum number of rows to return (optional, default None for all rows)
        :return:
        """

        # create a tweepy cursor to safely return the data
        curr = tweepy.Cursor(
            self.client.friends_ids,
            id_=id_,
            user_id=user_id,
            screen_name=screen_name

        )

        # page through it and parse results
        ds = []

        for friend in curr.items():
            ds.append(friend)

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    def followers_ids(self, id_=None, screen_name=None, user_id=None, limit=None):
        """
        Returns an array containing the IDs of users following the specified user.

        :param id_: Specifies the ID or screen name of the user.
        :param user_id: Specifies the ID of the user. Helpful for disambiguating when a valid user ID is also a valid screen name.
        :param screen_name: Specifies the screen name of the user. Helpful for disambiguating when a valid screen name is also a user ID.
        :param limit: the maximum number of rows to return (optional, default None for all rows)
        :return:
        """

        # create a tweepy cursor to safely return the data
        curr = tweepy.Cursor(
            self.client.followers_ids,
            id_=id_,
            user_id=user_id,
            screen_name=screen_name
        )

        # page through it and parse results
        ds = []
        for follower in curr.items():
            ds.append(follower)

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    # #################################################################
    # #####  List Methods                                         #####
    # #################################################################
    def list_timeline(self, owner, slug, since_id=None, max_id=None, limit=None):
        """
        Show tweet timeline for members of the specified list.

        :param owner: the screen name of the owner of the list
        :param slug: the slug name or numerical ID of the list
        :param limit: the maximum number of rows to return (optional, default None for all rows)
        :param since_id: Returns only statuses with an ID greater than (that is, more recent than) the specified ID.
        :param max_id: Returns only statuses with an ID less than (that is, older than) or equal to the specified ID.
        :return:
        """

        data = self.client.list_timeline(
            owner,
            slug,
            since_id=since_id,
            max_id=max_id
        )

        # page through it and parse results
        ds = []
        for timeline_item in data:
            # get the raw json, flatten it one layer and then discard anything nested farther
            ds.append(self._flatten_dict(timeline_item._json, layers=3, drop_deeper=True))

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    def get_list(self, owner=None, slug=None, limit=None):
        """
        Show the specified list. Private lists will only be shown if the authenticated user owns the specified list.

        :param owner: the screen name of the owner of the list
        :param slug: the slug name or numerical ID of the list
        :param limit: the maximum number of rows to return (optional, default None for all rows)
        :return:
        """

        data = self.client.get_list(
            owner,
            slug
        )

        # page through it and parse results
        ds = []
        for timeline_item in data:
            # get the raw json, flatten it one layer and then discard anything nested farther
            ds.append(self._flatten_dict(timeline_item._json, layers=3, drop_deeper=True))

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    def list_members(self, owner=None, slug=None, limit=None):
        """
        Returns the members of the specified list.

        :param owner: the screen name of the owner of the list
        :param slug: the slug name or numerical ID of the list
        :param limit: the maximum number of rows to return (optional, default None for all rows)
        :return:
        """

        # TODO: fix when it's fixed in tweepy: https://github.com/tweepy/tweepy/issues/697

        # create a tweepy cursor to safely return the data
        curr = tweepy.Cursor(
            self.client.get_list,
            owner=owner,
            slug=slug
        )

        ds = []

        for list_item in curr.items():
            # get the raw json, flatten it one layer and then discard anything nested farther
            ds.append(self._flatten_dict(list_item._json, layers=3, drop_deeper=True))

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    def list_subscribers(self, owner=None, slug=None, limit=None):
        """
        Returns the subscribers of the specified list.

        :param owner: the screen name of the owner of the list
        :param slug: the slug name or numerical ID of the list
        :param limit: the maximum number of rows to return (optional, default None for all rows)
        :return:
        """

        # TODO: fix when it's fixed in tweepy: https://github.com/tweepy/tweepy/issues/697

        # create a tweepy cursor to safely return the data
        curr = tweepy.Cursor(
            self.client.list_subscribers,
            owner=owner,
            slug=slug
        )

        # page through it and parse results
        ds = []
        for list_item in curr.items():
            # get the raw json, flatten it one layer and then discard anything nested farther
            ds.append(self._flatten_dict(list_item._json, layers=3, drop_deeper=True))

            if limit is not None:
                if len(ds) >= limit:
                    break

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    # #################################################################
    # #####  Status Methods                                       #####
    # #################################################################
    def get_status(self, id_):
        """
        Returns a single status specified by the ID parameter.

        :param id_: The numerical ID of the status.
        :return:
        """
        data = self.client.get_status(id_)

        ds = [self._flatten_dict(data._json, layers=3, drop_deeper=True)]

        # form the dataframe
        df = pd.DataFrame(ds)

        return df

    def retweets(self, id_=None, count=None):
        """
        Returns up to 100* of the first retweets of the given tweet.
        Please read the discrepancies below.

        DISCREPANCIES:
			- while the tweepy API states that the first 100 tweets are returned, testing shows that the limit actually seems to waver between 89-91
        	- testing shows that self.client.retweets always returns one less Status obect than specified in count
        	- if the count <1, the number of retweets returned is 19

        :param id_: The numerical ID of the status.
        :param count: Specifies the number of retweets to retrieve.
        """

        # count += 1 # if you want to make up for the second discrepancy
        data = self.client.retweets(id_, count)
        # print(len(data)) # if you want to examine the first discrepancy
        ds = []
        # page through it and parse the results
        for retweet in data:
            retweet.__dict__.pop('_api')

            # append retweet
            ds.append(self._flatten_dict(retweet._json, layers=3, drop_deeper=True))

        # form the dataframe
        df = pd.DataFrame(ds)
        return df
