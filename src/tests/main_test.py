import pytest
from unittest.mock import MagicMock
from main import (
    get_tags_for_all_buckets,
    handler,
    has_pii_content,
    my_list_bucket,
)


@pytest.fixture
def mock_s3():
    mock = MagicMock()
    mock.list_bucket.return_value = {
        "Buckets": [
            {"Name": f"string{i}", "CreationDate": "2015-09-14T20:00:00.000Z"}
            for i in range(6)
        ],
        "Owner": {"DisplayName": "string", "ID": "string"},
    }

    def get_bucket_tagging_responses(Bucket: str, *args, **kwargs):
        if "5" in Bucket:
            return {"TagSet": [{"Key": "pii", "Value": "true"}]}
        return {"TagSet": [{"Key": "pii", "Value": "false"}]}

    mock.get_bucket_tagging.side_effect = get_bucket_tagging_responses
    return mock


@pytest.fixture
def positive_pii_tags():
    return {"TagSet": [{"Key": "pii", "Value": "true"}]}


@pytest.fixture
def negative_pii_tags():
    return {"TagSet": [{"Key": "pii", "Value": "false"}]}


def test_list_bucket(mock_s3):
    # moderately complicated bucket list object, but not too bad.
    # We are duplicating info that was already set up in mock_s3 fixture.
    result = my_list_bucket(mock_s3)
    expected = {
        "Buckets": [
            {"Name": f"string{i}", "CreationDate": "2015-09-14T20:00:00.000Z"}
            for i in range(6)
        ],
        "Owner": {"DisplayName": "string", "ID": "string"},
    }
    assert result == expected


def test_get_tags_for_all_buckets(
    mock_s3, negative_pii_tags, positive_pii_tags
):
    buckets = my_list_bucket(mock_s3)["Buckets"]
    result = get_tags_for_all_buckets(buckets, mock_s3)
    expected = [negative_pii_tags for _ in range(5)] + [positive_pii_tags]
    assert result == expected


def test_has_pii_content(positive_pii_tags, negative_pii_tags):
    # Pretty straightforward to test in a naive way
    # These test cases will not find the bug in the bad impl of has_pii_content
    assert has_pii_content(positive_pii_tags) == True
    assert has_pii_content(negative_pii_tags) == False


def test_handler(mock_s3, mocker):
    mocker.patch("main.boto3.client", return_value=mock_s3)
    result = handler()
    assert result == 1  # expected bc of how we build mock_s3
