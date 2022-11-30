from src.system import System
import boto3, json, time
from pathlib import Path
from src.file_handling import load_file_to_dict
from src.version import Version
from src.utils import cfn_create_or_update, get_management_bucket_name, get_management_bucket_url
from src.region import Region

class Config():
    version : Version
    system : System
    env_type : str
    region : Region
    identifier : str
    account : str
    role_arn : str
    template_parameters : dict
    resource_overrides : dict

    def deploy(self, local_template_override:dict):
        '''
        Takes a cloudformation template from S3 and creates/updates the stack in AWS CloudFormation
        '''
        # Check parameters
        
        STACK_NAME = self.generate_stack_name()
        object_key = f'{self.system.name}/{self.system.version}'

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
        return [
            self.system.name,
            self.env_type,
            self.region,
            self.identifier
        ].join("-")

    @staticmethod
    def load_config_from_file(file_path:Path):
        config_dict = load_file_to_dict(file_path)
        return Config(
            version=Version(config_dict["Version"]),
            system=System(
                name=config_dict["System"]["Name"],
                version=Version(config_dict["System"]["Version"])
            ),
            env_type=config_dict["EnvType"],
            region=Region(config_dict["Region"]),
            identifier=config_dict["Identifier"],
            account=config_dict["Account"],
            role_arn=config_dict["RoleArn"],
            template_parameters=config_dict["TemplateParameters"],
            resource_overrides=config_dict["ResourceOverride"]
        )