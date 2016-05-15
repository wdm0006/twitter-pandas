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

    df = tp.home_timeline(limit=10)
    print(df.head())

    df = tp.statuses_lookup(id_=[x for x in df['id'].values], limit=10)
    print(df.head())

    df = tp.user_timeline(id_=user_id, limit=10)
    print(df.head())

    df = tp.retweets_of_me(limit=10)
    print(df.head())
