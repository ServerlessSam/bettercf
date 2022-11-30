import importlib, boto3, time, json
from pathlib import Path
from src import file_handling
from src.system import System
from src.config import Config
from src.utils import cfn_create_or_update, get_management_bucket_name
dfm = importlib.import_module("data-file-merge") #TODO remove this workaroudn when dfm v0.3 is released

class BetterCfInstance():

    '''
    Synopsis: 
        Deploys the init stack to the management AWS account. 
        This stack mostly contains the S3 bucket that future deployments will send their templates to.
    '''
    def initialise(self):
        STACK_NAME = "BetterCF-management"
        System.build(
            system_name="management",
            root_path_override=Path(__file__).parent.parent.joinpath(".management").resolve()
        )
        template = json.dumps(Path(__file__).parent.parent.joinpath(".management/output/management.json").resolve())
        
        #TODO address this when dfm v0.3 is released and build() returns the object too.
        #template = System.build(
        #     system_name="management",
        #     root_path_override=Path(__file__).parent.parent.joinpath(".management").resolve()
        # )

        boto3_kwargs = {
            "StackName" : STACK_NAME,
            "TemplateBody" : template,
            # "Capabilities" : [
            #     "CAPABILITY_AUTO_EXPAND",
            #     "CAPABILITY_NAMED_IAM"
            # ],
            "OnFailure" :'ROLLBACK',
        }

        cfn_create_or_update(STACK_NAME, boto3_kwargs)

    def teardown(self):
        BUCKET_NAME= get_management_bucket_name()
        STACK_NAME = "BetterCF-management"
        s3_client = boto3.client('s3')

        s3_client.delete_objects(
            Bucket=BUCKET_NAME,
            Delete={
                'Objects': [
                    {
                        'Key': '*'
                    },
                ],
            }
        )

        cf_client = boto3.client("cloudformation")
        cf_client.delete_stack(StackName=STACK_NAME)
        return