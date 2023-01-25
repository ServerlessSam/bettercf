from src.template import Template
from src.account import Account
import json
from pathlib import Path
from dfm.file_types import JsonFileType
from src.version import Version
from src.utils import cfn_create_or_update, get_management_bucket_url, is_non_empty_string
from src.region import Region
from dataclasses import dataclass, field

@dataclass
class Stack():
    version : Version
    template : Template
    template_version : Version
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
        object_key = f'{self.template.name}/{self.template_version.get_version_string()}'

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
            self.template.name,
            self.env_type,
            self.region.code,
            self.identifier
        ]).lower()

    @staticmethod
    def load_stack_config_from_file(file_path:Path):
        stack_config_dict = JsonFileType.load_from_file(file_path)

        # Check for unexpected keys
        ALL_EXPECTED_KEYS = [
            "Version",
            "Template",
            "EnvType",
            "Region",
            "Identifier",
            "RoleArn",
            "TemplateParameters",
            "ResourceOverrides"
        ]
        for key in stack_config_dict:
            if key not in ALL_EXPECTED_KEYS:
                raise Exception("Unexpected key '{key}' detected in stack config file.")

        # Check all expected keys are present
        for key in ALL_EXPECTED_KEYS:
            if key not in stack_config_dict:
                raise Exception(f"Stack Config Parsing Failure: Stack config file is missing required {key} key.")

        # String key checks
        STRING_KEYS=[
            "Version",
            "EnvType",
            "Region",
            "Identifier",
        ]

        for key in STRING_KEYS:
            if not is_non_empty_string(stack_config_dict[key]):
                raise Exception(f'Stack Config Parsing Failure: Stack config {key} value: {stack_config_dict[key]} must be a non-empty string.')
    
        # Template checks
        TEMPLATE_KEYS = ["Name", "Version"]
        for key in TEMPLATE_KEYS:
            if key not in stack_config_dict["Template"]:
                raise Exception(f"Stack Config Parsing Failure: Stack config file's Template is missing required {key} key.")
            if not is_non_empty_string(stack_config_dict["Template"][key]):
                raise Exception(f'Stack Config Parsing Failure: Stack config Template\'s {key} value: {stack_config_dict["Template"][key]} must be a non-empty string.')
        
        # Role Arn checks
        if not (is_non_empty_string(stack_config_dict["RoleArn"]) or stack_config_dict["RoleArn"] == None):
            raise Exception(f'Stack Config Parsing Failure: Stack config RoleArn value {stack_config_dict["RoleArn"]} must be a non-empty string or null.')

        # Dict key checks
        EXPECTED_DICT_KEYS = ["TemplateParameters", "ResourceOverrides"]
        for key in EXPECTED_DICT_KEYS:
            if not (type(stack_config_dict[key]) == dict or stack_config_dict[key] == None):
                raise Exception(f'Stack Config Parsing Failure: Stack config {key} value {str(stack_config_dict[key])} must be a dictionary or null.')

        return Stack(
            version=Version(stack_config_dict["Version"]),
            template=Template(
                template_name=stack_config_dict["Template"]["Name"]
            ),
            template_version=Version(stack_config_dict["Template"]["Version"]),
            env_type=stack_config_dict["EnvType"],
            region=Region(name=stack_config_dict["Region"]),
            identifier=stack_config_dict["Identifier"],
            #account=config_dict["Account"],
            role_arn=stack_config_dict["RoleArn"],
            template_parameters=stack_config_dict["TemplateParameters"],
            resource_overrides=stack_config_dict["ResourceOverrides"]
        )