import pytest

from twitterpandas import TwitterPandas


@pytest.fixture
def twitter_pandas():
    return object.__new__(TwitterPandas)


@pytest.mark.parametrize(
    "data,layers,drop_deeper,expected",
    [
        (
            {"id": 1, "screen_name": "example"},
            1,
            True,
            {"id": 1, "screen_name": "example"},
        ),
        (
            {"id": 1, "user": {"id": 2, "screen_name": "example"}},
            1,
            True,
            {"id": 1, "user.id": 2, "user.screen_name": "example"},
        ),
        (
            {
                "status": {
                    "id": 1,
                    "user": {
                        "screen_name": "example",
                        "profile": {"location": "internet"},
                    },
                }
            },
            2,
            True,
            {"status.id": 1, "status.user.screen_name": "example"},
        ),
        (
            {"hashtags": ["python", "pandas"], "user": {"roles": ["author"]}},
            1,
            True,
            {"hashtags": ["python", "pandas"], "user.roles": ["author"]},
        ),
    ],
    ids=["flat", "single-level", "drop-deeper", "preserve-lists"],
)
def test_flatten_dict(twitter_pandas, data, layers, drop_deeper, expected):
    assert twitter_pandas._flatten_dict(data, layers, drop_deeper) == expected
