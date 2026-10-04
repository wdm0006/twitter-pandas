"""Import and construct TwitterPandas from an installed distribution; run outside the checkout."""
from unittest import mock

import tweepy
import twitterpandas
from twitterpandas import TwitterPandas

assert "site-packages" in twitterpandas.__file__, twitterpandas.__file__

# Real OAuthHandler/API constructors; only the HTTP transport is blocked.
with mock.patch("requests.Session.request", side_effect=AssertionError("network call")):
    tp = TwitterPandas("token", "secret", "key", "consumer-secret")

assert isinstance(tp.client, tweepy.API)
print("smoke ok:", twitterpandas.__file__, "tweepy", tweepy.__version__)
