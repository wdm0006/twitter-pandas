"""
Unit tests for the User-section methods of TwitterPandas, with the tweepy
client fully mocked so no credentials or network access are required.
"""

import warnings
from unittest import mock

import pandas as pd
import pytest

from twitterpandas import TwitterPandas


def _make_client():
    """Build a TwitterPandas instance without running the tweepy constructor."""
    tp = TwitterPandas.__new__(TwitterPandas)
    tp.client = mock.MagicMock()
    return tp


class _FakeCursor:
    """Stand-in for tweepy.Cursor that yields a fixed list of items."""

    def __init__(self, items):
        self._items = items

    def items(self):
        return iter(self._items)


def _fake_user(user_id):
    obj = mock.MagicMock()
    obj._json = {'id': user_id, 'screen_name': 'user_%d' % user_id}
    return obj


def test_friends_returns_one_row_per_friend():
    tp = _make_client()

    friend_ids = [101, 102, 103]

    def fake_get_user(user_id=None, **kwargs):
        return pd.DataFrame([{'id': user_id, 'screen_name': 'user_%d' % user_id}])

    with mock.patch('twitterpandas.client.tweepy.Cursor', return_value=_FakeCursor(friend_ids)):
        with mock.patch.object(tp, 'get_user', side_effect=fake_get_user):
            df = tp.friends(screen_name='someone')

    assert len(df) == len(friend_ids)
    assert sorted(df['id'].tolist()) == sorted(friend_ids)


def test_friends_respects_limit():
    tp = _make_client()

    friend_ids = [101, 102, 103, 104, 105]

    def fake_get_user(user_id=None, **kwargs):
        return pd.DataFrame([{'id': user_id}])

    with mock.patch('twitterpandas.client.tweepy.Cursor', return_value=_FakeCursor(friend_ids)):
        with mock.patch.object(tp, 'get_user', side_effect=fake_get_user):
            df = tp.friends(screen_name='someone', limit=2)

    assert len(df) == 2
    assert df['id'].tolist() == [101, 102]


def test_search_users_no_limit_does_not_raise():
    tp = _make_client()

    users = [_fake_user(1), _fake_user(2)]

    with mock.patch('twitterpandas.client.tweepy.Cursor', return_value=_FakeCursor(users)):
        with warnings.catch_warnings():
            warnings.simplefilter('error')  # any warning would raise
            df = tp.search_users(query='x')

    assert len(df) == 2


def test_search_users_warns_over_1000():
    tp = _make_client()

    users = [_fake_user(i) for i in range(3)]

    with mock.patch('twitterpandas.client.tweepy.Cursor', return_value=_FakeCursor(users)):
        with pytest.warns(UserWarning):
            tp.search_users(query='x', limit=2000)
