import pytest, boto3
from moto import mock_s3, mock_cloudformation
from src.initialisation import BetterCfInstance

class TestInitialisation:

    @mock_cloudformation
    def test_initialize_happy_path(self, monkeypatch):
        
        mock_cfn_create_or_update_args = ()

        # Patch to skip create/update process as that isn't tested here. However we still want to verify it was called.
        def mock_cfn_create_or_update(STACK_NAME, boto3_kwargs):
            nonlocal mock_cfn_create_or_update_args 
            mock_cfn_create_or_update_args = (STACK_NAME, boto3_kwargs)
            pass

        monkeypatch.setattr("src.initialisation.cfn_create_or_update", mock_cfn_create_or_update)

        instance = BetterCfInstance()
        instance.initialise()

        assert mock_cfn_create_or_update_args[0] == "BetterCF-management"
        assert mock_cfn_create_or_update_args[1]["StackName"] == "BetterCF-management"

    @mock_s3
    @mock_cloudformation
    def test_teardown_happy_path_empty_bucket(self, monkeypatch):
        
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr("src.initialisation.get_management_bucket_name", get_mocked_management_bucket_name)

        # Create mocked S3 bucket
        s3_conn = boto3.client("s3", region_name="us-east-1")
        s3_conn.create_bucket(
            Bucket = get_mocked_management_bucket_name()
        )

        cf_conn = boto3.client("cloudformation")
        cf_conn.create_stack(
            StackName='BetterCF-management',
            TemplateBody='{"AWSTemplateFormatVersion":"2010-09-09","Description":"A test template","Resources":{},"Outputs":{}}'
        )

        instance = BetterCfInstance()
        instance.teardown()

        assert s3_conn.list_objects_v2(Bucket=get_mocked_management_bucket_name())["KeyCount"] == 0
        assert (
            cf_conn.list_stacks()["StackSummaries"][0]["StackName"],
            cf_conn.list_stacks()["StackSummaries"][0]["StackStatus"]
            ) == ("BetterCF-management", "DELETE_COMPLETE")

    @mock_s3
    @mock_cloudformation
    def test_teardown_happy_path(self, monkeypatch):
        
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr("src.initialisation.get_management_bucket_name", get_mocked_management_bucket_name)

        # Create mocked S3 bucket
        s3_conn = boto3.client("s3", region_name="us-east-1")
        s3_conn.create_bucket(
            Bucket = get_mocked_management_bucket_name()
        )

        s3_conn.put_object(
            Body = b'foo',
            Bucket = get_mocked_management_bucket_name(),
            Key = "foo/0.1"
        )

        cf_conn = boto3.client("cloudformation")
        cf_conn.create_stack(
            StackName='BetterCF-management',
            TemplateBody='{"AWSTemplateFormatVersion":"2010-09-09","Description":"A test template","Resources":{},"Outputs":{}}'
        )

        instance = BetterCfInstance()
        instance.teardown(empty_bucket_first=True)

        assert s3_conn.list_objects_v2(Bucket=get_mocked_management_bucket_name())["KeyCount"] == 0
        assert (
            cf_conn.list_stacks()["StackSummaries"][0]["StackName"],
            cf_conn.list_stacks()["StackSummaries"][0]["StackStatus"]
            ) == ("BetterCF-management", "DELETE_COMPLETE")

    @mock_s3
    @mock_cloudformation
    def test_teardown_not_initialised(self):
        instance = BetterCfInstance()
        with pytest.raises(Exception):
            instance.teardown()