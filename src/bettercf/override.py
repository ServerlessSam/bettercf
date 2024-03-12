def override_resources(resources:dict, overrides):
    """
    Synopsis: Overrides keys/values in a CloudFormation resource dictionary.
    It is possible to:
    - insert keys (>>)
    - delete keys (<<)
    - merge keys with already existing values (^^)

    To do this in the overrides dictionary:
    - include the full key/value tree to the key you'd like to override
      (the same tree found in the template "Resources" section).
    - Prefix the key name with either '>>','<<' or '^^' for the key in the tree that you'd like the insert/delete/merge to occur at.
    - The function handles nested values beyond the indicated key so there complete flexibility to override however you like.

    Note:
    - You can insert keys with any value type.
    - You can delete keys with any value type (you don't even need to specify the value in the override dict).
    - You can only merge keys if their value is a dict or list (not int, string, null etc).

    Parameters:
    - resources : the resource dictionary found in a CloudFormation template at the "Resources" key.
    - overrides : either a list or dictionary specifying what overrides you would like to apply.

    Example:
    The following ResourceOverrides in a Citadel configuration file:

    ...

    "ResourceOverrides" : {
        "LoaderPiiTokenEmisLambdaFunction": {
            "Properties": {
                "Environment": {
                    "Variables": {
                        ">>NEW_SALT_SECRET_NAME": {
                            "Ref": "NewPiiSalt"
                        },
                        "DATABASE_HOST": {
                            "^^Fn::GetAtt": [
                                "something_new"
                            ]
                        }
                    }
                }
            }
        }
    }

    ...

    produces this:

    ...

    "LoaderPiiTokenEmisLambdaFunction": {
            ...
                "Environment": {
                    "Variables": {
                        ...
                        "DATABASE_HOST": {
                            "Fn::GetAtt": [
                                "RdsDbInstance",
                                "Endpoint.Address",
                                "something_new"
                            ]
                        },
                        "NEW_SALT_SECRET_NAME": {
                            "Ref": "NewPiiSalt"
                        }
                    }

    ...

    instead of:

    ...

    "LoaderPiiTokenEmisLambdaFunction": {	
            ...
                "Environment": {	
                    "Variables": {	
                        ...
                        "DATABASE_HOST": {	
                            "Fn::GetAtt": [	
                                "RdsDbInstance",	
                                "Endpoint.Address"	
                            ]	
                        }	
                    }

    ...

    Returns:
    The new resources dict including overrides.
    """
    if type(overrides) == dict:
        for resource_key, resource_obj in overrides.items():

            # A key is found that needs to be added/replaced.
            if resource_key.startswith(">>"):
                print(f"overwritting {resource_key}")
                resources[resource_key.replace(">>", "")] = resource_obj

            # A key is found that needs to be deleted.
            elif resource_key.startswith("<<"):
                if resource_key.replace("<<", "") in resources:
                    print(f"deleting {resource_key}")
                    del resources[resource_key.replace("<<", "")]
                else:
                    raise Exception(f"Trying to delete key: {resource_key.replace('<<', '')} but it is not found in resources.")

            # A key is found that needs to be merged.
            elif resource_key.startswith("^^"):
                print(f"merging {resource_key}")
                if type(resource_obj) == dict:
                    resources[resource_key.replace("^^", "")] = {**resources[resource_key.replace("^^", "")], **resource_obj}
                elif type(resource_obj) == list:
                    resources[resource_key.replace("^^", "")] = resources[resource_key.replace("^^", "")] + resource_obj
                else:
                    raise Exception(f"Trying to merge a non list/dict ({type(resource_obj)}")

            # The key did not require any operations. Now we rerun the function with the nested object from this key.
            elif resource_key in resources:
                nested_result = override_resources(resources[resource_key], resource_obj)

    # ?
    elif type(overrides) == list:
        for override in overrides:
            list_result = override_resources(resources, override)

    return resources

def count_overrides_in_dict(overrides):
    '''
    Synposis: Returns the number of overrides found in an override dict. It has no use for now but may be handy in future
    '''
    overrides_found = 0
    if type(overrides) == dict:
        for resource_key, resource_obj in overrides.items():

            if resource_key.startswith(">>") or resource_key.startswith("<<") or resource_key.startswith("^^"):
                overrides_found = overrides_found + 1
            
            overrides_found = overrides_found + count_overrides_in_dict(resource_obj)

    elif type(overrides) == list:
        for override in overrides:
            overrides_found = overrides_found +  count_overrides_in_dict(override)
    return overrides_found