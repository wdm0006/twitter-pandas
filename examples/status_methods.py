from twitterpandas import TwitterPandas
from examples.keys import TWITTER_OAUTH_SECRET, TWITTER_OAUTH_TOKEN, TWITTER_CONSUMER_SECRET, TWITTER_CONSUMER_KEY

__author__ = 'keyanvakil'

if __name__ == '__main__':
	# create a twitter pandas client object
	tp = TwitterPandas(
	    TWITTER_OAUTH_TOKEN,
	    TWITTER_OAUTH_SECRET,
	    TWITTER_CONSUMER_KEY,
 	    TWITTER_CONSUMER_SECRET
	)

	user_id = tp.api_id

	# example tweet with >100 retweets
	# https://twitter.com/BoredElonMusk/status/611549517322715136
	tweet = 611549517322715136
	
	# second example tweet with >100 retweets
	# https://twitter.com/jack/status/20
	# tweet = 20

	df = tp.get_status(id_=tweet)
	print(df.head())
	print('\n')
	print(df.info())
	print('\n\n')

	# return dataframe with info on first five retweets
	df = tp.retweets(id_=tweet, count= 5)
	print(df.head())
	print('\n')
	print(df.info())
	print('\n\n')
