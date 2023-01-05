import boto3
from pathlib import Path
from src.utils import cfn_create_or_update, get_management_bucket_name
from dfm.config import BuildConfig

class BetterCfInstance():

    '''
    Synopsis: 
        Deploys the init stack to the management AWS account. 
        This stack mostly contains the S3 bucket that future deployments will send their templates to.
    '''
    def initialise(self):
        STACK_NAME = "BetterCF-management"

        cfg = BuildConfig.load_config_from_file(
            file_path=Path(__file__).parent.parent.joinpath(".dfm/template_builder.json").resolve(),
            root_path=Path(__file__).parent.parent.joinpath(".management").resolve(),
            parameters={
                "SystemName" : "bettercf-management"
            }
        )
        template = cfg.build()

        boto3_kwargs = {
            "StackName" : STACK_NAME,
            "TemplateBody" : str(template),
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
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(BUCKET_NAME)
        bucket.object_versions.delete()
        cf_client = boto3.client("cloudformation")
        cf_client.delete_stack(StackName=STACK_NAME)
        return