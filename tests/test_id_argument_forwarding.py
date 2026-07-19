"""Tests for translating public ``id_`` arguments at the Tweepy boundary."""

from unittest import mock

import pytest

from twitterpandas import TwitterPandas


class _EmptyCursor:
    def items(self):
        return iter(())


def _make_client():
    tp = TwitterPandas.__new__(TwitterPandas)
    tp.client = mock.MagicMock()
    return tp


@pytest.mark.parametrize(
    'method_name, endpoint_name, extra_kwargs',
    [
        ('followers', 'followers', {}),
        ('friends', 'friends_ids', {}),
        ('user_timeline', 'user_timeline', {'since_id': 10, 'max_id': 20}),
        ('friends_friendships', 'friends_ids', {}),
        ('followers_friendships', 'followers_ids', {}),
    ]
)
def test_cursor_user_selectors_use_tweepy_id(method_name, endpoint_name, extra_kwargs):
    tp = _make_client()

    with mock.patch('twitterpandas.client.tweepy.Cursor', return_value=_EmptyCursor()) as cursor:
        getattr(tp, method_name)(
            id_=123,
            user_id=456,
            screen_name='example',
            **extra_kwargs
        )

    endpoint = getattr(tp.client, endpoint_name)
    forwarded = cursor.call_args
    assert forwarded.args == (endpoint,)
    assert forwarded.kwargs['id'] == 123
    assert 'id_' not in forwarded.kwargs
    assert forwarded.kwargs['user_id'] == 456
    assert forwarded.kwargs['screen_name'] == 'example'


def test_get_user_uses_tweepy_id_and_preserves_none_selectors():
    tp = _make_client()
    user = mock.MagicMock()
    user._json = {'id': 123}
    tp.client.get_user.return_value = user

    tp.get_user(id_=123)

    tp.client.get_user.assert_called_once_with(
        id=123,
        user_id=None,
        screen_name=None
    )


def test_statuses_lookup_keeps_tweepy_id_():
    tp = _make_client()
    tp.client.statuses_lookup.return_value = []

    tp.statuses_lookup(id_=[101, 102])

    tp.client.statuses_lookup.assert_called_once_with(
        id_=[101, 102],
        include_entities=None,
        trim_user=None
    )
