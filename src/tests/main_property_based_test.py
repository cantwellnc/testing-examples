from typing import Literal, TypedDict, Optional
from unittest.mock import MagicMock
import hypothesis.strategies as st
from hypothesis import given, assume, settings
import pytest
from main import handler, has_pii_content
from pytest_mock import mocker, module_mocker
from random import sample


deterministic_bucket_list = {
    "Buckets": [
        {"Name": f"string{i}", "CreationDate": "2015-09-14T20:00:00.000Z"}
        for i in range(6)
    ],
    "Owner": {"DisplayName": "string", "ID": "string"},
}


@st.composite
def random_list_bucket_response(draw):
    return draw(
        st.builds(
            dict,
            Buckets=st.lists(
                st.builds(
                    dict, Name=st.text(min_size=1), CreationDate=st.datetimes()
                )
            ),
            Owner=st.just({"DisplayName": "string", "ID": "string"}),
        ),
    )


def random_pii():
    return st.booleans().map(lambda x: str(x).lower())


def all_pii():
    return st.just("true")


def no_pii():
    return st.just("false")


@st.composite
def random_tags_object(draw, str_bool_val):
    # builds a random tags object
    str_boolean = draw(str_bool_val())
    random_pii_tag = draw(st.just({"Key": "pii", "Value": str_boolean}))
    other_tags = draw(
        st.lists(st.builds(dict, Key=st.text(), Value=st.text()))
    )
    tags = sample(other_tags + [random_pii_tag], len(other_tags) + 1)
    return draw(st.just({"TagSet": tags}))


@st.composite
def random_bucket_responses(draw, pii_regime):
    buckets = draw(random_list_bucket_response())
    num_buckets = len(buckets["Buckets"])
    tags = draw(
        st.lists(
            random_tags_object(pii_regime),
            min_size=num_buckets,  # adding these bounds sped up generation like crazy!
            max_size=num_buckets,
        )
    )
    assume(len(buckets["Buckets"]) == len(tags))
    return buckets, tags


@pytest.fixture(scope="module")
def mock_s3():
    # Partially random bucket information (only buckets; tags are still hardcoded)
    def inner(random_bucket_list):
        mock = MagicMock()
        mock.list_buckets.return_value = random_bucket_list

        def get_bucket_tagging_responses(Bucket: str, *args, **kwargs):
            if "5" in Bucket:
                return {"TagSet": [{"Key": "pii", "Value": "true"}]}
            return {"TagSet": [{"Key": "pii", "Value": "false"}]}

        mock.get_bucket_tagging.side_effect = get_bucket_tagging_responses
        return mock

    return inner


@pytest.fixture(scope="module")
def mock_s3_with_random_tags_and_buckets():
    # Totally random bucket information
    def inner(rand_buckets, rand_tags):
        mock = MagicMock()
        mock.list_buckets.return_value = rand_buckets
        mock.get_bucket_tagging.side_effect = rand_tags
        return mock

    return inner


@given(tags=random_tags_object(random_pii))
def test_has_pii_content_random(tags):
    # this doesn't catch the bug
    has_pii_content(tags)  # call, don't assert


@given(tags=random_tags_object(no_pii))
def test_no_pii(tags):
    # this doesn't catch the bug
    assert not has_pii_content(tags)


@given(tags=random_tags_object(all_pii))
def test_has_pii_content(tags):
    # THIS ONE DOES!
    assert has_pii_content(tags)


#     Falsifying example: test_has_pii_content(
#            tags={'TagSet': [{'Key': '', 'Value': ''},
#              {'Key': 'pii', 'Value': 'true'},
#              {'Key': '', 'Value': ''}]},
#    )


@given(rand_response=random_list_bucket_response())
def test_handler_returns_int(module_mocker, mock_s3, rand_response):
    client = mock_s3(rand_response)
    module_mocker.patch("main.boto3.client", return_value=client)
    result = handler()
    assert isinstance(result, int)
    assert result >= 0
    assert result <= len(client.list_buckets()["Buckets"])


@given(rand_responses=random_bucket_responses(random_pii))
def test_handler_fully_random_client(
    module_mocker, mock_s3_with_random_tags_and_buckets, rand_responses
):
    client = mock_s3_with_random_tags_and_buckets(*rand_responses)
    module_mocker.patch("main.boto3.client", return_value=client)
    result = handler()
    assert isinstance(result, int)
    assert result >= 0
    assert result <= len(client.list_buckets()["Buckets"])


def test_handler_some_buckets_have_pii(mock_s3, mocker):
    client = mock_s3(deterministic_bucket_list)
    mocker.patch("main.boto3.client", return_value=client)
    result = handler()
    assert result == 1


# Unrelated example of building data from a class
@given(st.data())
def test_build_class(data):
    class Event(TypedDict):
        region: Literal["us-east-1", "us-east-1"]
        account: str
        detail: dict
        is_async_invocation: bool

    print(data.draw(st.from_type(Event)))
