import boto3
import pytest
from moto import mock_cloudformation, mock_s3, mock_ssm

from src.bettercf.utils import (
    cfn_create_or_update,
    cfn_delete_stack,
    get_latest_version,
    get_management_bucket_location,
    get_management_bucket_name,
    get_management_bucket_url,
    is_non_empty_string,
)


class TestUtils:
    def test_get_latest_version_happy_path(self):
        versions = ["0.1", "0.2", "0.3"]
        assert get_latest_version(versions) == "0.3"

    def test_get_latest_version_with_micro_happy_path(self):
        versions = ["0.1.1", "0.1.2", "0.2.0"]
        assert get_latest_version(versions) == "0.2.0"

    def test_get_latest_version_bad_list(self):
        versions = [
            "0.1",
            "foo",
            "bar",
        ]
        with pytest.raises(Exception):
            get_latest_version(versions)

    def test_get_latest_version_empty_list_element(self):
        versions = [
            "0.1",
            "",
            None,
        ]
        with pytest.raises(Exception):
            get_latest_version(versions)

    @mock_s3
    def test_get_management_bucket_location_initialized_us_east_1(self, monkeypatch):
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr(
            "src.utils.get_management_bucket_name", get_mocked_management_bucket_name
        )
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=get_mocked_management_bucket_name())
        assert get_management_bucket_location() == "us-east-1"

    @mock_s3
    def test_get_management_bucket_location_initialized_non_default_region(
        self, monkeypatch
    ):
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr(
            "src.utils.get_management_bucket_name", get_mocked_management_bucket_name
        )
        conn = boto3.client("s3", region_name="eu-west-2")
        conn.create_bucket(
            Bucket=get_mocked_management_bucket_name(),
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        assert get_management_bucket_location() == "eu-west-2"

    @mock_s3
    def test_get_management_bucket_location_not_initialized(self, monkeypatch):
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr(
            "src.utils.get_management_bucket_name", get_mocked_management_bucket_name
        )

        with pytest.raises(Exception):
            get_management_bucket_location()

    @mock_ssm
    def test_get_management_bucket_name_initialized(self):
        conn = boto3.client("ssm")
        conn.put_parameter(
            Name="/BetterCF/.management/BetterCF-management-bucket-name",
            Type="String",
            Value="foo",
        )

        assert get_management_bucket_name() == "foo"

    @mock_ssm
    def test_get_management_bucket_name_not_initialized(self):
        with pytest.raises(Exception):
            get_management_bucket_name()

    @mock_ssm
    @mock_s3
    def test_get_management_bucket_url_initialized(self):
        ssm_conn = boto3.client("ssm")
        ssm_conn.put_parameter(
            Name="/BetterCF/.management/BetterCF-management-bucket-name",
            Type="String",
            Value="foo",
        )
        s3_conn = boto3.client("s3", region_name="us-east-1")
        s3_conn.create_bucket(Bucket="foo")

        assert get_management_bucket_url() == "https://foo.s3.us-east-1.amazonaws.com"

    @mock_ssm
    @mock_s3
    def test_get_management_bucket_url_not_initialized(self):
        with pytest.raises(Exception):
            get_management_bucket_url()

    @mock_cloudformation
    def test_cfn_create_or_update_no_stacks(self):
        cfn_create_or_update(
            StackName="foo",
            boto3_kwargs={
                "StackName": "foo",
                "TemplateBody": '{"AWSTemplateFormatVersion":"2010-09-09","Description":"A test template","Resources":{},"Outputs":{}}',
                "TimeoutInMinutes": 30,
                "Capabilities": ["CAPABILITY_AUTO_EXPAND", "CAPABILITY_NAMED_IAM"],
                "OnFailure": "ROLLBACK",
            },
        )
        conn = boto3.client("cloudformation")
        assert conn.list_stacks()["StackSummaries"][0]["StackName"] == "foo"

    @mock_cloudformation
    def test_cfn_create_or_update_existing_stacks(self):
        cfn_create_or_update(
            StackName="foo",
            boto3_kwargs={
                "StackName": "foo",
                "TemplateBody": '{"AWSTemplateFormatVersion":"2010-09-09","Description":"A test template","Resources":{},"Outputs":{}}',
                "TimeoutInMinutes": 30,
                "Capabilities": ["CAPABILITY_AUTO_EXPAND", "CAPABILITY_NAMED_IAM"],
                "OnFailure": "ROLLBACK",
            },
        )
        cfn_create_or_update(
            StackName="foo",
            boto3_kwargs={
                "StackName": "foo",
                "TemplateBody": '{"AWSTemplateFormatVersion":"2010-09-09","Description":"A test template","Resources":{},"Outputs":{}}',
                "TimeoutInMinutes": 30,
                "Capabilities": ["CAPABILITY_AUTO_EXPAND", "CAPABILITY_NAMED_IAM"],
                "OnFailure": "ROLLBACK",
            },
        )
        conn = boto3.client("cloudformation")
        assert conn.list_stacks()["StackSummaries"][0]["StackName"] == "foo"

    @mock_cloudformation
    def test_cfn_delete_stack_happy_path(self):
        cfn_create_or_update(
            StackName="foo",
            boto3_kwargs={
                "StackName": "foo",
                "TemplateBody": '{"AWSTemplateFormatVersion":"2010-09-09","Description":"A test template","Resources":{},"Outputs":{}}',
                "TimeoutInMinutes": 30,
                "Capabilities": ["CAPABILITY_AUTO_EXPAND", "CAPABILITY_NAMED_IAM"],
                "OnFailure": "ROLLBACK",
            },
        )
        cfn_delete_stack("foo")
        conn = boto3.client("cloudformation")
        assert (
            conn.list_stacks()["StackSummaries"][0]["StackStatus"] == "DELETE_COMPLETE"
        )

    def test_is_non_empty_string_happy_path(self):
        string = "foo"
        assert is_non_empty_string(string) is True

    def test_is_non_empty_string_max_length_happy_path(self):
        string = "foo"
        assert is_non_empty_string(string, 3) is True
        assert is_non_empty_string(string, 4) is True

    def test_is_non_empty_string_max_length_too_long(self):
        string = "foo"
        assert is_non_empty_string(string, 2) is False

    def test_is_non_empty_string_empty_string_fails(self):
        string = ""
        assert is_non_empty_string(string) is False
        assert is_non_empty_string(string, 3) is False

    def test_is_non_empty_string_null_string_fails(self):
        string = None
        assert is_non_empty_string(string) is False
        assert is_non_empty_string(string, 3) is False

    def test_is_non_empty_string_dict_input_fails(self):
        string = {"foo", "bar"}
        assert is_non_empty_string(string) is False
        assert is_non_empty_string(string, 99) is False
