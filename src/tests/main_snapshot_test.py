import pytest
from unittest.mock import MagicMock
from main import (
    get_tags_for_all_buckets,
    handler,
    has_pii_content,
    my_list_bucket,
)
from syrupy.assertion import SnapshotAssertion


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


def test_list_bucket(snapshot: SnapshotAssertion, mock_s3):
    assert snapshot == my_list_bucket(mock_s3)


def test_get_tags_for_all_buckets(snapshot: SnapshotAssertion, mock_s3):
    buckets = my_list_bucket(mock_s3)["Buckets"]
    result = get_tags_for_all_buckets(buckets, mock_s3)
    assert snapshot == result


def test_has_pii_content(
    snapshot: SnapshotAssertion, positive_pii_tags, negative_pii_tags
):
    # not really useful to test w snapshot since the output data structure is so simple
    assert has_pii_content(positive_pii_tags) == snapshot
    assert has_pii_content(negative_pii_tags) == snapshot


def test_handler(snapshot: SnapshotAssertion, mock_s3, mocker):
    mocker.patch("main.boto3.client", return_value=mock_s3)
    result = handler()
    assert result == snapshot  # expected bc of how we build mock_s3
