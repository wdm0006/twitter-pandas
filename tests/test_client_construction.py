from unittest import mock

from twitterpandas import TwitterPandas


def _build(**kwargs):
    with mock.patch("tweepy.OAuthHandler") as handler, mock.patch("tweepy.API") as api:
        tp = TwitterPandas("tok", "sec", "ckey", "csec", **kwargs)
    return tp, handler, api


def test_custom_timeout_is_forwarded_to_tweepy_api():
    tp, handler, api = _build(timeout=7)

    assert api.call_args.kwargs["timeout"] == 7
    assert api.call_args.args == (handler.return_value,)
    assert tp.client is api.return_value
    handler.assert_called_once_with("ckey", "csec")
    handler.return_value.set_access_token.assert_called_once_with("tok", "sec")


def test_default_timeout_is_sixty_seconds():
    _, _, api = _build()

    assert api.call_args.kwargs["timeout"] == 60
