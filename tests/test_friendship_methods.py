"""Network-free tests for friendship aggregation methods."""

from types import SimpleNamespace
from unittest import mock

import pandas as pd
import pytest

from twitterpandas import TwitterPandas


class _FakeCursor:
    def __init__(self, items):
        self._items = items

    def items(self):
        return iter(self._items)


def _make_client():
    tp = TwitterPandas.__new__(TwitterPandas)
    tp.client = mock.MagicMock()
    return tp


def _friendship(source_id, target_id):
    source = SimpleNamespace(
        id=source_id,
        id_str=str(source_id),
        screen_name='source_%d' % source_id,
        followed_by=target_id % 2 == 0,
        following=True,
        blocked_by=False,
        blocking=False,
        can_dm=target_id % 2 == 0,
    )
    target = SimpleNamespace(
        id=target_id,
        id_str=str(target_id),
        screen_name='target_%d' % target_id,
        following=target_id % 2 == 0,
        followed_by=True,
    )
    return source, target


@pytest.mark.parametrize(
    'method_name, endpoint_name',
    [
        ('friends_friendships', 'friends_ids'),
        ('followers_friendships', 'followers_ids'),
    ],
)
def test_rich_friendships_return_every_relationship(method_name, endpoint_name):
    tp = _make_client()
    relationship_ids = [101, 102, 103]
    tp.client.show_friendship.side_effect = [
        _friendship(7, target_id) for target_id in relationship_ids
    ]

    with mock.patch(
        'twitterpandas.client.tweepy.Cursor',
        return_value=_FakeCursor(relationship_ids),
    ) as cursor:
        result = getattr(tp, method_name)(id_=7, rich=True)

    assert result['target_user_id'].tolist() == relationship_ids
    assert result['target_user_screen_name'].tolist() == [
        'target_101',
        'target_102',
        'target_103',
    ]
    assert result['target_follows_source'].tolist() == [False, True, False]
    assert result.index.tolist() == [0, 1, 2]
    assert tp.client.show_friendship.call_count == 3
    cursor.assert_called_once_with(
        getattr(tp.client, endpoint_name),
        id=7,
        user_id=None,
        screen_name=None,
    )


@pytest.mark.parametrize(
    'method_name',
    ['friends_friendships', 'followers_friendships'],
)
def test_rich_friendships_return_empty_dataframe_for_empty_cursor(method_name):
    tp = _make_client()

    with mock.patch(
        'twitterpandas.client.tweepy.Cursor',
        return_value=_FakeCursor([]),
    ):
        result = getattr(tp, method_name)(id_=7, rich=True)

    assert result.empty
    assert isinstance(result, pd.DataFrame)
    tp.client.show_friendship.assert_not_called()


@pytest.mark.parametrize(
    'method_name',
    ['friends_friendships', 'followers_friendships'],
)
def test_sparse_friendships_preserve_ids_and_limit(method_name):
    tp = _make_client()

    with mock.patch(
        'twitterpandas.client.tweepy.Cursor',
        return_value=_FakeCursor([101, 102, 103]),
    ):
        result = getattr(tp, method_name)(id_=7, limit=2)

    assert result.to_dict('list') == {'id': [101, 102]}
    tp.client.show_friendship.assert_not_called()


@pytest.mark.parametrize(
    'method_name',
    ['friends_friendships', 'followers_friendships'],
)
def test_rich_friendships_preserve_limit(method_name):
    tp = _make_client()
    tp.client.show_friendship.side_effect = [
        _friendship(7, target_id) for target_id in [101, 102]
    ]

    with mock.patch(
        'twitterpandas.client.tweepy.Cursor',
        return_value=_FakeCursor([101, 102, 103]),
    ):
        result = getattr(tp, method_name)(id_=7, limit=2, rich=True)

    assert result['target_user_id'].tolist() == [101, 102]
    assert tp.client.show_friendship.call_count == 2
