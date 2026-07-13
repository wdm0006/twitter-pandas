from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock

from twitterpandas import TwitterPandas


class DirectMessageMethodsTestCase(TestCase):
    def setUp(self):
        self.twitter_pandas = TwitterPandas.__new__(TwitterPandas)
        self.twitter_pandas.client = Mock()

    @staticmethod
    def message():
        return SimpleNamespace(
            created_at='2016-01-01',
            id=123,
            id_str='123',
            text='hello \U0001f600',
            entities={
                'urls': [{'url': 'https://example.com'}],
                'user_mentions': [],
                'hashtags': [{'text': 'example'}],
            },
            sender=SimpleNamespace(_json={'id': 1, 'screen_name': 'sender'}),
            recipient=SimpleNamespace(_json={'id': 2, 'screen_name': 'recipient'}),
        )

    def test_default_paths_return_message_rows(self):
        message = self.message()
        self.twitter_pandas.client.direct_messages.return_value = [message]
        self.twitter_pandas.client.get_direct_message.return_value = message
        self.twitter_pandas.client.sent_direct_messages.return_value = [message]

        frames = [
            self.twitter_pandas.direct_messages(),
            self.twitter_pandas.get_direct_message(id_=123),
            self.twitter_pandas.sent_direct_messages(),
        ]

        for frame in frames:
            self.assertEqual(len(frame), 1)
            self.assertEqual(frame.loc[0, 'created_at'], '2016-01-01')
            self.assertEqual(frame.loc[0, 'id'], 123)
            self.assertEqual(frame.loc[0, 'id_str'], '123')
            self.assertEqual(frame.loc[0, 'entities.urls_url'], 'https://example.com')
            self.assertEqual(frame.loc[0, 'entities.hashtags_text'], 'example')
            self.assertNotIn('sender_id', frame.columns)

    def test_include_user_data_keeps_enriched_columns(self):
        message = self.message()
        self.twitter_pandas.client.direct_messages.return_value = [message]
        self.twitter_pandas.client.get_direct_message.return_value = message
        self.twitter_pandas.client.sent_direct_messages.return_value = [message]

        frames = [
            self.twitter_pandas.direct_messages(include_user_data=True),
            self.twitter_pandas.get_direct_message(id_=123, include_user_data=True),
            self.twitter_pandas.sent_direct_messages(include_user_data=True),
        ]

        for frame in frames:
            self.assertEqual(len(frame), 1)
            self.assertEqual(frame.loc[0, 'sender_screen_name'], 'sender')
            self.assertEqual(frame.loc[0, 'recipient_screen_name'], 'recipient')
            self.assertEqual(frame.loc[0, 'full_text'], 'hello \ufffd')
