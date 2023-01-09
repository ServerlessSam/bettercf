from src.system import System
from src.version import Version
from moto import mock_s3
import boto3, pytest, os, json
from src import utils
from pathlib import Path

class TestSystem:

    def test_system_init_default_config_path(self):
        sys = System(
            system_name="foo",
            version=Version("0.1"),
        )
        assert sys.dfm_config.destination_file.location.path == "${SYSTEM_NAME}.json"

    @mock_s3
    def test_detect_latest_version_happy_path(self, monkeypatch):

        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr("src.system.get_management_bucket_name", get_mocked_management_bucket_name)

        # Create mocked S3 bucket
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(
            Bucket = get_mocked_management_bucket_name()
        )
        conn.put_object(
            Body = b'foo',
            Bucket = get_mocked_management_bucket_name(),
            Key = "foo/0.1"
        )
        assert System.detect_latest_version("foo") == "0.1"

    @mock_s3
    def test_detect_latest_version_empty_bucket(self, monkeypatch):

        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr("src.system.get_management_bucket_name", get_mocked_management_bucket_name)

        # Create mocked S3 bucket
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(
            Bucket = get_mocked_management_bucket_name()
        )
        with pytest.raises(Exception):
            System.detect_latest_version("foo")

    @mock_s3
    def test_detect_latest_version_bad_version_name(self, monkeypatch):

        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr("src.system.get_management_bucket_name", get_mocked_management_bucket_name)

        # Create mocked S3 bucket
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(
            Bucket = get_mocked_management_bucket_name()
        )
        conn.put_object(
            Body = b'foo',
            Bucket = get_mocked_management_bucket_name(),
            Key = "foo/0.1"
        )
        conn.put_object(
            Body = b'bar',
            Bucket = get_mocked_management_bucket_name(),
            Key = "foo/bar"
        )
        with pytest.raises(Exception):
            System.detect_latest_version("foo")

    
    def test_build_happy_path(self):
        sys = System(
            system_name="foo",
            version=Version("0.1"),
            dfm_root_path=Path(__file__).parent.joinpath("test_systems")
        )

        built = sys.build()
        os.remove(str(sys.dfm_config.destination_file.location.root_path / "foo.json")) #TODO add option to dfm.config.build() to not write to file and use this instead.

        assert "FooBucket" in built["Resources"]
        assert "AWSTemplateFormatVersion" in built

    @mock_s3
    def test_push_happy_path(self, monkeypatch):
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr("src.system.get_management_bucket_name", get_mocked_management_bucket_name)

        # Create mocked S3 bucket
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(
            Bucket = get_mocked_management_bucket_name()
        )
        conn.put_object(
            Body = b'foo',
            Bucket = get_mocked_management_bucket_name(),
            Key = "foo/0.1"
        )
        
        sys = System(
            system_name="foo",
            dfm_root_path=Path(__file__).parent.joinpath("test_systems")
        )
        sys.push("foo")

        obj_in_s3 = conn.get_object(
            Bucket = get_mocked_management_bucket_name(),
            Key = "foo/0.2"
        )["Body"].read()

        assert obj_in_s3 == b"foo"

    mock_s3
    def test_build_and_push_happy_path(self, monkeypatch):
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr("src.system.get_management_bucket_name", get_mocked_management_bucket_name)

        # Create mocked S3 bucket
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(
            Bucket = get_mocked_management_bucket_name()
        )
        conn.put_object(
            Body = b'foo',
            Bucket = get_mocked_management_bucket_name(),
            Key = "foo/0.1"
        )
        
        sys = System(
            system_name="foo",
            dfm_root_path=Path(__file__).parent.joinpath("test_systems")
        )
        sys.build()
        sys.push()

        os.remove(str(sys.dfm_config.destination_file.location.root_path / "foo.json")) #TODO add option to dfm.config.build() to not write to file and use this instead.


        obj_in_s3 = json.loads(conn.get_object(
            Bucket = get_mocked_management_bucket_name(),
            Key = "foo/0.2"
        )["Body"].read())

        assert "FooBucket" in obj_in_s3["Resources"]
        assert "AWSTemplateFormatVersion" in obj_in_s3