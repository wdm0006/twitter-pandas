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

    df = tp.followers(limit=10)
    print(df.head())

    df = tp.me()
    print(df)

    df = tp.get_user(screen_name='willmcginnis')
    print(df)

    df = tp.search_users(query='willmcginnis', limit=10)
    print(df)