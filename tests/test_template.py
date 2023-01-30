import json
import os
from pathlib import Path

import boto3
import pytest
from moto import mock_s3

from src.template import Template


class TestTemplate:
    def test_template_init_default_config_path(self):
        sys = Template(template_name="foo")
        assert sys.dfm_config.destination_file.location.path == "${TEMPLATE_NAME}.json"

    @mock_s3
    def test_detect_latest_version_happy_path(self, monkeypatch):
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr(
            "src.template.get_management_bucket_name", get_mocked_management_bucket_name
        )

        # Create mocked S3 bucket
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=get_mocked_management_bucket_name())
        conn.put_object(
            Body=b"foo", Bucket=get_mocked_management_bucket_name(), Key="foo/0.1"
        )
        assert Template.detect_latest_version("foo") == "0.1"

    @mock_s3
    def test_detect_latest_version_empty_bucket(self, monkeypatch):
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr(
            "src.template.get_management_bucket_name", get_mocked_management_bucket_name
        )

        # Create mocked S3 bucket
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=get_mocked_management_bucket_name())
        with pytest.raises(Exception):
            Template.detect_latest_version("foo")

    @mock_s3
    def test_detect_latest_version_bad_version_name(self, monkeypatch):
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr(
            "src.template.get_management_bucket_name", get_mocked_management_bucket_name
        )

        # Create mocked S3 bucket
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=get_mocked_management_bucket_name())
        conn.put_object(
            Body=b"foo", Bucket=get_mocked_management_bucket_name(), Key="foo/0.1"
        )
        conn.put_object(
            Body=b"bar", Bucket=get_mocked_management_bucket_name(), Key="foo/bar"
        )
        with pytest.raises(Exception):
            Template.detect_latest_version("foo")

    def test_build_happy_path(self):
        sys = Template(
            template_name="foo",
            dfm_root_path=Path(__file__).parent.joinpath("test_templates"),
        )

        built = sys.build()
        os.remove(
            str(sys.dfm_config.destination_file.location.root_path / "foo.json")
        )  # TODO add option to dfm.config.build() to not write to file and use this instead.

        assert "FooBucket" in built["Resources"]
        assert "AWSTemplateFormatVersion" in built

    @mock_s3
    def test_push_happy_path(self, monkeypatch):
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr(
            "src.template.get_management_bucket_name", get_mocked_management_bucket_name
        )

        # Create mocked S3 bucket
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=get_mocked_management_bucket_name())
        conn.put_object(
            Body=b"foo", Bucket=get_mocked_management_bucket_name(), Key="foo/0.1"
        )

        sys = Template(
            template_name="foo",
            dfm_root_path=Path(__file__).parent.joinpath("test_templates"),
        )
        sys.push(template_str="foo")

        obj_in_s3 = conn.get_object(
            Bucket=get_mocked_management_bucket_name(), Key="foo/0.2"
        )["Body"].read()

        assert obj_in_s3 == b"foo"

    @mock_s3
    def test_build_and_push_happy_path(self, monkeypatch):
        def get_mocked_management_bucket_name():
            return "cf-management-bucket-123456789"

        monkeypatch.setattr(
            "src.template.get_management_bucket_name", get_mocked_management_bucket_name
        )

        # Create mocked S3 bucket
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=get_mocked_management_bucket_name())
        conn.put_object(
            Body=b"foo", Bucket=get_mocked_management_bucket_name(), Key="foo/0.1"
        )

        sys = Template(
            template_name="foo",
            dfm_root_path=Path(__file__).parent.joinpath("test_templates"),
        )
        sys.build()
        sys.push()

        os.remove(
            str(sys.dfm_config.destination_file.location.root_path / "foo.json")
        )  # TODO add option to dfm.config.build() to not write to file and use this instead.

        obj_in_s3 = json.loads(
            conn.get_object(Bucket=get_mocked_management_bucket_name(), Key="foo/0.2")[
                "Body"
            ].read()
        )

        assert "FooBucket" in obj_in_s3["Resources"]
        assert "AWSTemplateFormatVersion" in obj_in_s3
