from real_src.system import System
import boto3, json, time
from pathlib import Path
from real_src.file_handling import load_file_to_dict

class Config():
    version : str
    system : System
    env_type : str
    region : str
    identifier : str
    account : str
    role_arn : str
    template_parameters : dict
    resource_overrides : dict

    def auto_increment_config_version(self):

        return #str

    def deploy(self):
        '''
        Takes a cloudformation template from S3 and creates/updates the stack in AWS CloudFormation
        '''
        # Check parameters
        #config = load_file_to_dict("/".join([cloudscripts_root_path, "cloudformation_configurations", f"{config_file_name}.json"]))
        
        full_stack_name = f'{self.system.name}-{self.env_type}-euw2-{self.identifier}'
        object_key = f'{self.system.name}/{self.system.version}.json'
        BUCKET_NAME = "" #TODO
        additional_parameters = []
        for parameter_key, parameter_value in self.template_parameters.items():
            additional_parameters.append(
                {
                    'ParameterKey': parameter_key,
                    'ParameterValue': parameter_value,
                    'UsePreviousValue': False,
                }
            )
        # Trigger stack creation in CloudFormation.
        self.create_stack(template_uri=template_uri)

    def generate_stack_name(self):
        return [
            self.system.name,
            self.env_type,
            self.region,
            self.identifier
        ].join("-")

    def create_stack(self, template:dict=None, template_uri:str=None):
        STACK_NAME = self.generate_stack_name()
        if bool(template is None) & bool(template_uri is None):
            raise Exception("Cannot supply 'template' and 'template_uri' parameters to 'create_stack' function. Only supply one.")
        elif bool(template is not None) & bool(template_uri is not None):
            raise Exception("Must supply either 'template' or 'template_uri' parameter to 'create_stack' function. Neither were supplied.")
        client = boto3.client('cloudformation')

        boto3_kwargs = {
            "StackName" : STACK_NAME,
            "TemplateBody" : json.dumps(template),
            "TimeoutInMinutes" : 30,
            "Capabilities" : [
                "CAPABILITY_AUTO_EXPAND",
                "CAPABILITY_NAMED_IAM"
            ],
            "OnFailure" :'ROLLBACK',
        }

        # Add custom parameters to the boto3 API call if neccessary.
        if self.template_parameters:
            boto3_kwargs["Parameters"] = self.template_parameters

        # Add role arn kwarg if it has been set by the caller
        if self.role_arn:
            boto3_kwargs["RoleARN"] = self.role_arn

        try:
            client.get_template(StackName=STACK_NAME)

            # If get_template does not error, the stack already exists so we need to update_stack
            print(f"Beginning CloudFormation template update for {STACK_NAME}")
            boto3_function = client.update_stack
            boto3_kwargs.pop("TimeoutInMinutes")
            boto3_kwargs.pop("OnFailure")

        # If ClientError if thrown, the stack doesn't exist yet and we need to create_stack
        except client.exceptions.ClientError:
            print(f"Beginning CloudFormation template creation for {STACK_NAME}")
            boto3_function = client.create_stack

        if template:
            boto3_function(**boto3_kwargs)
        elif template_uri:
            boto3_kwargs["TemplateURL"] = template_uri
            boto3_kwargs.pop("TemplateBody")
            boto3_function(**boto3_kwargs)
        else:
            raise Exception("Something went wrong, one of 'template' or 'template_url' must be supplied to 'create_stack'. This exception should have been handled earlier but has not.")

        stack_state = "IN_PROGRESS"
        while "IN_PROGRESS" in stack_state:
            time.sleep(5)
            stack_state = client.describe_stacks(
                StackName=STACK_NAME
            )["Stacks"][0]["StackStatus"]

        if stack_state not in ["CREATE_COMPLETE", "UPDATE_COMPLETE"] :
            raise Exception(f"Stack creation failed: {stack_state}")
        else:
            print(f"Stack '{STACK_NAME}' created/updated successfully.")

    @staticmethod
    def load_config_from_file(file_path:Path):
        config_dict = load_file_to_dict(file_path)
        return Config(
            version=config_dict["Version"],
            system=System(
                name=config_dict["System"]["Name"],
                version=config_dict["System"]["Version"]
            ),
            env_type=config_dict["EnvType"],
            region=config_dict["Region"],
            identifier=config_dict["Identifier"],
            account=config_dict["Account"],
            role_arn=config_dict["RoleArn"],
            template_parameters=config_dict["TemplateParameters"],
            resource_overrides=config_dict["ResourceOverride"]
        )