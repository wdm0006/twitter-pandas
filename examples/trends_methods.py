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

    print('\n\nTRENDS AVAILABLE')
    df = tp.trends_available()
    print(df.shape)

    print('\n\nTRENDS PLACE')
    df = tp.trends_place(id_=1)
    print(df.shape)

    print('\n\nTRENDS CLOSEST')
    df = tp.trends_closest(lat=33.74, long=84.38)
    print(df.shape)