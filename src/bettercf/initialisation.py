from pathlib import Path

import boto3
from dfm.config import BuildConfig

from bettercf.utils import cfn_create_or_update, cfn_delete_stack, get_management_bucket_name


class BetterCfInstance:

    """
    Synopsis:
        Deploys the init stack to the management AWS account.
        This stack mostly contains the S3 bucket that future deployments will send their templates to.
    """

    def initialise(self, mode: str = "STANDARD"):
        STACK_NAME = "BetterCF-management"

        cfg = BuildConfig.load_config_from_file(
            file_path=Path(__file__)
            .parent.parent.joinpath(".dfm/template_builder.json")
            .resolve(),
            root_path=Path(__file__).parent.parent.joinpath(".management").resolve(),
            parameters={"TemplateName": "bettercf-management"},
        )

        template = cfg.build(save_to_local_file=False)

        boto3_kwargs = {
            "StackName": STACK_NAME,
            "TemplateBody": str(template),
            "Parameters": [
                {
                    "ParameterKey": "BucketType",
                    "ParameterValue": mode,
                }
            ],
            # "Capabilities" : [
            #     "CAPABILITY_AUTO_EXPAND",
            #     "CAPABILITY_NAMED_IAM"
            # ],
            "OnFailure": "ROLLBACK",
        }

        cfn_create_or_update(STACK_NAME, boto3_kwargs)

    def teardown(self, empty_bucket_first: bool = False):
        BUCKET_NAME = get_management_bucket_name()
        STACK_NAME = "BetterCF-management"
        if empty_bucket_first:
            s3 = boto3.resource("s3")
            bucket = s3.Bucket(BUCKET_NAME)
            bucket.object_versions.delete()  # Note this will fail for governance mode buckets
        cfn_delete_stack(STACK_NAME)
        return
