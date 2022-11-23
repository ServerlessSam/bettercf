import importlib, boto3, time, json
from pathlib import Path
from real_src import file_handling
from real_src.system import System
from real_src.config import Config
dfm = importlib.import_module("data-file-merge") #TODO remove this workaroudn when dfm v0.3 is released


class ProjectInitialisation():

    def initialise(self):
        BUCKET_NAME = ""
        STACK_NAME = "cf-management"
        System.build(
            system_name="management",
            root_path_override=Path(__file__).parent.parent.child(".management").resolve()
        )
        template = json.dumps(Path(__file__).parent.parent.child(".management").child("output").child("management.json").resolve())
        client = boto3.client('cloudformation')

        boto3_kwargs = {
            "StackName" : STACK_NAME,
            "TemplateBody" : template,
            "TimeoutInMinutes" : 30,
            "Capabilities" : [
                "CAPABILITY_AUTO_EXPAND",
                "CAPABILITY_NAMED_IAM"
            ],
            "OnFailure" :'ROLLBACK',
        }


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

            boto3_function(**boto3_kwargs)

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

    def teardown(self):
        BUCKET_NAME = ""
        s3_client = boto3.client('s3')

        #TODO empty bucket
        
        s3_client.delete_bucket(Bucket=BUCKET_NAME)
        return