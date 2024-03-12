import pytest

'''
This file contains common formats of CloudFormation resource values. I.E the 'value' from:
    {
        "ResourceName" : {
            <Resource Dict>
        }
    }
These dictionaries are passed into unit tests of the override_resource() function.
'''

@pytest.fixture
def original_resource_dict():
    original_resource_dict = {
        "ParentKey" : {
            "OldKey" :{
                "OldNestedKey" : "OldNestedValue"
            }
        }
    }
    yield original_resource_dict

@pytest.fixture
def original_resource_dict_four_keys():
    original_resource_dict_four_keys = {
        "ParentKey" : {
            "OldKey1" :{
                "OldNestedKey" : "OldNestedValue"
            },
            "OldKey2" :{
                "OldNestedKey" : "OldNestedValue"
            },
            "OldKey3" :{
                "OldNestedKey" : "OldNestedValue"
            },
            "OldKey4" :{
                "OldNestedKey" : "OldNestedValue"
            }
        }
    }
    yield original_resource_dict_four_keys

@pytest.fixture
def original_resource_dict_four_elements():
    original_resource_dict_four_elements = {
        "ParentKey" : [
            {
                "OldKey1" :{
                    "OldNestedKey" : "OldNestedValue"
                }
            },
            {
                "OldKey2" :{
                    "OldNestedKey" : "OldNestedValue"
                }
            },
            {
                "OldKey3" :{
                    "OldNestedKey" : "OldNestedValue"
                }
            },
            {
                "OldKey4" :{
                    "OldNestedKey" : "OldNestedValue"
                }
            }
        ]
    }
    yield original_resource_dict_four_elements


@pytest.fixture
def original_resource_dict_string_and_int():
    original_resource_dict_string_and_int = {
        "String" : "string",
        "Int" : 123,
        "None" : None
    }
    yield original_resource_dict_string_and_int