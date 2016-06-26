from twitterpandas import TwitterPandas
from examples.keys import TWITTER_OAUTH_SECRET, TWITTER_OAUTH_TOKEN, TWITTER_CONSUMER_SECRET, TWITTER_CONSUMER_KEY

__author__ = 'willmcginnis'

if __name__ == '__main__':
    tp = TwitterPandas(
        TWITTER_OAUTH_TOKEN,
        TWITTER_OAUTH_SECRET,
        TWITTER_CONSUMER_KEY,
        TWITTER_CONSUMER_SECRET
    )

    user_id = tp.api_id

    df = tp.lists()
    print(df.head())

    df = tp.lists_memberships()
    print(df.head())

    df = tp.lists_subscriptions()
    print(df.head()) # returning empty

    df = tp.list_timeline(owner='knanne', slug='data-science', limit=5)
    print(df.head())

    # TODO: broken in tweepy: https://github.com/tweepy/tweepy/issues/697
    # df = tp.get_list(owner='knanne', slug='data-science', limit=5)
    # print(df.head())
    #
    # df = tp.list_subscribers(owner='knanne', slug='data-science', limit=5)
    # print(df.head())
