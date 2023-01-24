from src.config import Config
from src.region import Region
from src.version import Version
from src.system import System
from pathlib import Path
import pytest
class TestConfig:

    def test_load_config_from_file_happy_path(self):
        cfg = Config.load_config_from_file(Path(__file__).parent.joinpath("test_configs/config.json"))

        assert cfg.env_type == "Prod"
        assert cfg.identifier == "bar"
        assert cfg.region.full_name == Region(name="eu-west-2").full_name
        assert cfg.version.get_version_string() == Version("1.0").get_version_string()
        assert cfg.template_parameters == {}
        assert cfg.resource_overrides == {}
        assert not cfg.role_arn
        assert cfg.system.name == System(system_name="foo").name
        assert cfg.system_version.get_version_string() == Version("0.1").get_version_string()

    def test_load_config_from_file_missing_some_attributes_errors(self):
        with pytest.raises(Exception):
            Config.load_config_from_file(Path(__file__).parent.joinpath("test_configs/config_incomplete.json"))

    def test_load_config_from_missing_file(self):
        with pytest.raises(Exception):
            Config.load_config_from_file(Path(__file__).parent.joinpath("test_configs/MISSING!_config.json"))

    def test_generate_stack_name_happy_path(self):
        cfg = Config.load_config_from_file(Path(__file__).parent.joinpath("test_configs/config.json"))

        assert cfg.generate_stack_name() == "foo-prod-euw2-bar"

    def test_load_config_from_file_with_bad_values(self):
        for file_name in [
            "config_blank_env_type",
            "config_blank_id",
            "config_blank_region",
            "config_blank_role_arn",
            "config_blank_system_name",
            "config_blank_system_version",
            "config_blank_version"
        ]:
            with pytest.raises(Exception):
                print(file_name)
                Config.load_config_from_file(Path(__file__).parent.joinpath(f"test_configs/{file_name}.json"))

    def test_deploy_happy_path(self, monkeypatch):
        def get_mocked_management_bucket_url():
            return "https://cf-management-bucket-123456789.s3.us-east-1.amazonaws.com"

        monkeypatch.setattr("src.config.get_management_bucket_url", get_mocked_management_bucket_url)

        mock_cfn_create_or_update_args = ()

        # Patch to skip create/update process as that isn't tested here. However we still want to verify it was called.
        def mock_cfn_create_or_update(STACK_NAME, boto3_kwargs):
            nonlocal mock_cfn_create_or_update_args 
            mock_cfn_create_or_update_args = (STACK_NAME, boto3_kwargs)
            pass

        monkeypatch.setattr("src.config.cfn_create_or_update", mock_cfn_create_or_update)

        cfg = Config.load_config_from_file(Path(__file__).parent.joinpath("test_configs/config.json"))
        cfg.deploy()

        assert mock_cfn_create_or_update_args[0] == "foo-prod-euw2-bar"
        assert mock_cfn_create_or_update_args[1]["StackName"] == "foo-prod-euw2-bar"
        assert mock_cfn_create_or_update_args[1]["TemplateURL"] == "https://cf-management-bucket-123456789.s3.us-east-1.amazonaws.com/foo/0.1"

    def test_deploy_local_template_override_happy_path(self, monkeypatch):
        def get_mocked_management_bucket_url():
            return "https://cf-management-bucket-123456789.s3.us-east-1.amazonaws.com"

        monkeypatch.setattr("src.config.get_management_bucket_url", get_mocked_management_bucket_url)

        mock_cfn_create_or_update_args = ()

        # Patch to skip create/update process as that isn't tested here. However we still want to verify it was called.
        def mock_cfn_create_or_update(STACK_NAME, boto3_kwargs):
            nonlocal mock_cfn_create_or_update_args 
            mock_cfn_create_or_update_args = (STACK_NAME, boto3_kwargs)
            pass

        monkeypatch.setattr("src.config.cfn_create_or_update", mock_cfn_create_or_update)

        cfg = Config.load_config_from_file(Path(__file__).parent.joinpath("test_configs/config.json"))
        cfg.deploy(local_template_override={"foo":"bar"})

        assert mock_cfn_create_or_update_args[1]["TemplateBody"] == '{"foo": "bar"}'
        assert "TemplateURL" not in mock_cfn_create_or_update_args[1]

    def test_deploy_with_role_arn_happy_path(self, monkeypatch):
        def get_mocked_management_bucket_url():
            return "https://cf-management-bucket-123456789.s3.us-east-1.amazonaws.com"

        monkeypatch.setattr("src.config.get_management_bucket_url", get_mocked_management_bucket_url)

        mock_cfn_create_or_update_args = ()

        # Patch to skip create/update process as that isn't tested here. However we still want to verify it was called.
        def mock_cfn_create_or_update(STACK_NAME, boto3_kwargs):
            nonlocal mock_cfn_create_or_update_args 
            mock_cfn_create_or_update_args = (STACK_NAME, boto3_kwargs)
            pass

        monkeypatch.setattr("src.config.cfn_create_or_update", mock_cfn_create_or_update)

        cfg = Config.load_config_from_file(Path(__file__).parent.joinpath("test_configs/config.json"))
        cfg.role_arn = "foo"
        cfg.deploy()

        assert mock_cfn_create_or_update_args[1]["RoleARN"] == "foo"

    def test_deploy_with_template_parameters_happy_path(self, monkeypatch):
        def get_mocked_management_bucket_url():
            return "https://cf-management-bucket-123456789.s3.us-east-1.amazonaws.com"

        monkeypatch.setattr("src.config.get_management_bucket_url", get_mocked_management_bucket_url)

        mock_cfn_create_or_update_args = ()

        # Patch to skip create/update process as that isn't tested here. However we still want to verify it was called.
        def mock_cfn_create_or_update(STACK_NAME, boto3_kwargs):
            nonlocal mock_cfn_create_or_update_args 
            mock_cfn_create_or_update_args = (STACK_NAME, boto3_kwargs)
            pass

        monkeypatch.setattr("src.config.cfn_create_or_update", mock_cfn_create_or_update)

        cfg = Config.load_config_from_file(Path(__file__).parent.joinpath("test_configs/config.json"))
        cfg.template_parameters = {"foo":"bar"}
        cfg.deploy()

        assert mock_cfn_create_or_update_args[1]["Parameters"] == [{'ParameterKey': 'foo', 'ParameterValue': 'bar', 'UsePreviousValue': False}]


        
