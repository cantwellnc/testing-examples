import boto3
from mypy_boto3_s3 import S3Client
from mypy_boto3_s3.type_defs import (
    ListBucketsOutputTypeDef,
    GetBucketTaggingOutputTypeDef,
)

# Made up task: write a script that returns the # of buckets with PII
# (Personally Identifying Information) in an AWS account,
#  based on a 'pii' tag.


def my_list_bucket(client: S3Client) -> ListBucketsOutputTypeDef:
    return client.list_buckets()


def get_tags_for_all_buckets(
    buckets: list, client: S3Client
) -> list[GetBucketTaggingOutputTypeDef]:
    return [
        client.get_bucket_tagging(Bucket=bucket["Name"]) for bucket in buckets
    ]


def has_pii_content(bucket_tags: GetBucketTaggingOutputTypeDef) -> bool:
    # pii tag is of form {"Key": "pii", "Value": "true | false"}
    # intentionally bad implementation
    return bucket_tags["TagSet"][0]["Value"] == "true"
    # a better implementation
    # for tag in bucket_tags["TagSet"]:
    #     if tag["Key"] == "pii" and tag["Value"] == "true":
    #         return True
    # return False


def handler():
    # imagine this being the handler of a lambda that is running in your account
    # to document this info on a daily basis
    client = boto3.client("s3")
    buckets = my_list_bucket(client)
    tags = get_tags_for_all_buckets(buckets["Buckets"], client)
    return sum([has_pii_content(tag) for tag in tags])
