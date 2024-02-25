import time

import boto3

from bettercf.version import Version


def get_latest_version(versions: list[str]):
    try:  # TODO this assumed that all versions are of the same syntax. Perhaps we need a better check?
        return max(versions, key=Version.major_minor)
    except Exception:
        pass  # TODO I don't think this is a good pattern
    try:
        return max(versions, key=Version.major_minor_micro)
    except Exception:
        raise Exception(
            f"Versions (e.g '{versions[0]}' are not of the 'X.Y' or 'X.Y.Z' format"
        )


def get_management_bucket_name():
    client = boto3.client("ssm")
    try:
        to_return = client.get_parameter(
            Name="/BetterCF/.management/BetterCF-management-bucket-name",
        )["Parameter"]["Value"]
        return to_return
    except Exception:
        raise Exception("Hmm")  # TODO


def get_management_bucket_location():
    client = boto3.client("s3")
    bucket_name = get_management_bucket_name()
    try:
        to_return = client.get_bucket_location(Bucket=bucket_name)["LocationConstraint"]
        return (
            to_return if to_return else "us-east-1"
        )  # As per AWS docs, a null response = us-east-1
    except Exception:
        raise Exception("Hmmmmm")  # TODO


def get_management_bucket_url():
    bucket_name = get_management_bucket_name()
    bucket_region = get_management_bucket_location()
    return f"https://{bucket_name}.s3.{bucket_region}.amazonaws.com"


def cfn_create_or_update(StackName: str, boto3_kwargs: dict):
    try:
        client = boto3.client("cloudformation")
        client.get_template(StackName=StackName)

        # If get_template does not error, the stack already exists so we need to update_stack
        print(f"Beginning CloudFormation template update for {StackName}")
        boto3_function = client.update_stack
        boto3_kwargs.pop("OnFailure")

    # If ClientError if thrown, the stack doesn't exist yet and we need to create_stack
    except client.exceptions.ClientError:
        print(f"Beginning CloudFormation template creation for {StackName}")
        boto3_function = client.create_stack

        boto3_function(**boto3_kwargs)

    stack_state = "IN_PROGRESS"
    while "IN_PROGRESS" in stack_state:
        time.sleep(5)
        stack_state = client.describe_stacks(StackName=StackName)["Stacks"][0][
            "StackStatus"
        ]

    if stack_state not in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]:
        raise Exception(f"Stack creation failed: {stack_state}")
    else:
        print(f"Stack '{StackName}' created/updated successfully.")


def cfn_delete_stack(StackName: str):
    client = boto3.client("cloudformation")
    if len(client.describe_stacks(StackName=StackName)["Stacks"]) != 1:
        raise Exception(
            f"Expected exactly one instance of {StackName} stack. Instead {len(client.describe_stacks(StackName=StackName)['Stacks'])} were found."
        )
    stack_id = client.describe_stacks(StackName=StackName)["Stacks"][0]["StackId"]

    client.delete_stack(StackName=StackName)
    stack_state = "IN_PROGRESS"

    while "IN_PROGRESS" in stack_state:
        time.sleep(5)
        stack_state = client.describe_stacks(StackName=stack_id)["Stacks"][0][
            "StackStatus"
        ]
    if stack_state in ["DELETE_COMPLETE"]:
        print(f"Stack '{StackName}' deleted successfully.")
    else:
        raise Exception(f"Stack deletion failed: {stack_state}")


def is_non_empty_string(string: str, max_length: int = None):
    if not (type(string) == str and string):
        return False
    elif max_length:
        if len(string) > max_length:
            return False
    return True
