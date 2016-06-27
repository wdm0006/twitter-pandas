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

	df = tp.followers_ids(id_ = user_id, limit = 10)
	print(df.head())
	print('\n')
	print(df.info())
	print('\n\n')

	df = tp.friends_ids(id_ = user_id, limit = 10)
	print(df.head())
	print('\n')
	print(df.info())
	print('\n\n')

	friend_id = df[0][0]
	print('friend_id =', str(friend_id))
	print('\n')

	print("Does user_id follow friend_id?")
	print(tp.exists_friendship(source_id = user_id, target_id = friend_id))
	print('\n\n')

	df = tp.show_friendship(source_id = user_id, target_id = friend_id)
	print(df.head())
	print('\n')
	print(df.info())
	print('\n\n')
