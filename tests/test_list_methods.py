"""List endpoint forwarding and DataFrame regression tests."""

from types import SimpleNamespace
from unittest import mock

import pandas as pd
import pytest

from twitterpandas import TwitterPandas


def _make_client():
    tp = TwitterPandas.__new__(TwitterPandas)
    tp.client = mock.MagicMock()
    return tp


@pytest.mark.parametrize('method_name', ['list_members', 'list_subscribers', 'list_timeline'])
def test_list_cursor_endpoint_and_keywords(method_name):
    tp = _make_client()
    rows = [
        SimpleNamespace(_json={'id': 1, 'user': {'screen_name': 'first'}}),
        SimpleNamespace(_json={'id': 2, 'user': {'screen_name': 'second'}})
    ]
    extra_kwargs = {'since_id': 10, 'max_id': 20} if method_name == 'list_timeline' else {}

    with mock.patch('twitterpandas.client.tweepy.Cursor') as cursor:
        cursor.return_value.items.return_value = iter(rows)
        if method_name == 'list_timeline':
            frame = tp.list_timeline('x', 'y', limit=1, **extra_kwargs)
        else:
            frame = getattr(tp, method_name)(owner='x', slug='y', limit=1)

    assert cursor.call_args.args == (getattr(tp.client, method_name),)
    assert cursor.call_args.kwargs == dict(owner_screen_name='x', slug='y', **extra_kwargs)
    assert 'owner' not in cursor.call_args.kwargs
    cursor.return_value.items.assert_called_once_with()
    pd.testing.assert_frame_equal(
        frame, pd.DataFrame([{'id': 1, 'user.screen_name': 'first'}]), check_like=True
    )


def test_get_list_keywords_and_single_model_frame():
    tp = _make_client()
    tp.client.get_list.return_value = SimpleNamespace(
        _json={'id': 42, 'slug': 'y', 'user': {'screen_name': 'x'}}
    )

    frame = tp.get_list(owner='x', slug='y', limit=0)

    tp.client.get_list.assert_called_once_with(owner_screen_name='x', slug='y')
    assert 'owner_id' not in tp.client.get_list.call_args.kwargs
    pd.testing.assert_frame_equal(
        frame, pd.DataFrame([{'id': 42, 'slug': 'y', 'user.screen_name': 'x'}]), check_like=True
    )
