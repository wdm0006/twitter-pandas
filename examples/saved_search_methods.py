from twitterpandas import TwitterPandas
from examples.keys import TWITTER_OAUTH_SECRET, TWITTER_OAUTH_TOKEN, TWITTER_CONSUMER_SECRET, TWITTER_CONSUMER_KEY

__author__ = 'freddievargus'

if __name__ == '__main__':
    tp = TwitterPandas(
        TWITTER_OAUTH_TOKEN,
        TWITTER_OAUTH_SECRET,
        TWITTER_CONSUMER_KEY,
        TWITTER_CONSUMER_SECRET
    )

    df = tp.saved_searches()
    print(df.head(), '\n')
    print(df.info(), '\n\n')

    search_id = df[['id_str']].values[0][0]
    df = tp.get_saved_search(search_id)
    print(df, '\n')
    print(df.info())
