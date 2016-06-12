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

    data = tp.client.direct_messages()
    qrs = data[0].__dict__
    print(qrs) # print out one object as an example

