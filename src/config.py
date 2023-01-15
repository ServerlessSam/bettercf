from src.system import System
from src.account import Account
import json
from pathlib import Path
from dfm.file_types import JsonFileType
from src.version import Version
from src.utils import cfn_create_or_update, get_management_bucket_url, is_non_empty_string
from src.region import Region
from dataclasses import dataclass, field

@dataclass
class Config():
    version : Version
    system : System
    env_type : str
    region : Region
    identifier : str
    #account : Account
    role_arn : str=None
    template_parameters : dict=field(default_factory=dict)
    resource_overrides : dict=field(default_factory=dict)

    #TODO add stack tags with version being deployed
    def deploy(self, local_template_override:dict=None):
        '''
        Takes a cloudformation template from S3 and creates/updates the stack in AWS CloudFormation
        '''
        # Check parameters
        
        STACK_NAME = self.generate_stack_name()
        object_key = f'{self.system.name}/{self.system.version.get_version_string()}'

        boto3_kwargs = {
            "StackName" : STACK_NAME,
            "TemplateURL" : f"{get_management_bucket_url()}/{object_key}",
            "TimeoutInMinutes" : 30,
            "Capabilities" : [
                "CAPABILITY_AUTO_EXPAND",
                "CAPABILITY_NAMED_IAM"
            ],
            "OnFailure" :'ROLLBACK',
        }

        parameters = []
        for parameter_key, parameter_value in self.template_parameters.items():
            parameters.append(
                {
                    'ParameterKey': parameter_key,
                    'ParameterValue': parameter_value,
                    'UsePreviousValue': False,
                }
            )
        if parameters:
            boto3_kwargs["Parameters"] = parameters

        # Add role arn kwarg if it has been set by the caller
        if self.role_arn:
            boto3_kwargs["RoleARN"] = self.role_arn

        if local_template_override:
            boto3_kwargs["TemplateBody"] = json.dumps(local_template_override)
            boto3_kwargs.pop("TemplateURL")

        cfn_create_or_update(STACK_NAME, boto3_kwargs)

    def generate_stack_name(self):
        return "-".join([
            self.system.name,
            self.env_type,
            self.region.code,
            self.identifier
        ]).lower()

    @staticmethod
    def load_config_from_file(file_path:Path):
        config_dict = JsonFileType.load_from_file(file_path)

        # Check for unexpected keys
        ALL_EXPECTED_KEYS = [
            "Version",
            "System",
            "EnvType",
            "Region",
            "Identifier",
            "RoleArn",
            "TemplateParameters",
            "ResourceOverrides"
        ]
        for key in config_dict:
            if key not in ALL_EXPECTED_KEYS:
                raise Exception("Unexpected key '{key}' detected in config file.")

        # Check all expected keys are present
        for key in ALL_EXPECTED_KEYS:
            if key not in config_dict:
                raise Exception(f"Config Parsing Failure: Config file is missing required {key} key.")

        # String key checks
        STRING_KEYS=[
            "Version",
            "EnvType",
            "Region",
            "Identifier",
        ]

        for key in STRING_KEYS:
            if not is_non_empty_string(config_dict[key]):
                raise Exception(f'Config Parsing Failure: Config {key} value: {config_dict[key]} must be a non-empty string.')
    
        # System checks
        SYSTEM_KEYS = ["Name", "Version"]
        for key in SYSTEM_KEYS:
            if key not in config_dict["System"]:
                raise Exception(f"Config Parsing Failure: Config file's System is missing required {key} key.")
            if not is_non_empty_string(config_dict["System"][key]):
                raise Exception(f'Config Parsing Failure: Config system\'s {key} value: {config_dict["System"][key]} must be a non-empty string.')
        
        # Role Arn checks
        if not (is_non_empty_string(config_dict["RoleArn"]) or config_dict["RoleArn"] == None):
            raise Exception(f'Config Parsing Failure: Config RoleArn value {config_dict["RoleArn"]} must be a non-empty string or null.')

        # Dict key checks
        EXPECTED_DICT_KEYS = ["TemplateParameters", "ResourceOverrides"]
        for key in EXPECTED_DICT_KEYS:
            if not (type(config_dict[key]) == dict or config_dict[key] == None):
                raise Exception(f'Config Parsing Failure: Config {key} value {str(config_dict[key])} must be a dictionary or null.')

        return Config(
            version=Version(config_dict["Version"]),
            system=System(
                system_name=config_dict["System"]["Name"],
                version=Version(config_dict["System"]["Version"])
            ),
            env_type=config_dict["EnvType"],
            region=Region(name=config_dict["Region"]),
            identifier=config_dict["Identifier"],
            #account=config_dict["Account"],
            role_arn=config_dict["RoleArn"],
            template_parameters=config_dict["TemplateParameters"],
            resource_overrides=config_dict["ResourceOverrides"]
        )