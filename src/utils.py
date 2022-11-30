from src.version import Version
import boto3, time

def get_latest_version(versions:list(str)):
        if Version.major_minor(versions[0]): #TODO this assumed that all versions are of the same syntax. Perhaps we need a better check?
            return max(versions, key=Version.major_minor)
        elif Version.major_minor_micro(versions[0]):
            return max(versions, key=Version.major_minor_micro)
        else:
            raise Exception(f"Versions (e.g '{versions[0]}' are not of the 'X.Y' or 'X.Y.Z' format")

def get_management_bucket_name():
    return

def get_management_bucket_url():
    return

def cfn_create_or_update(StackName:str, boto3_kwargs:dict):
    try:
        client = boto3.client('cloudformation')
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
        stack_state = client.describe_stacks(
            StackName=StackName
        )["Stacks"][0]["StackStatus"]

    if stack_state not in ["CREATE_COMPLETE", "UPDATE_COMPLETE"] :
        raise Exception(f"Stack creation failed: {stack_state}")
    else:
        print(f"Stack '{StackName}' created/updated successfully.")