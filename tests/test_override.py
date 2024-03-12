from bettercf.override import *
import pytest

class TestCommon:
    def test_override_resource_new_dict_key(self, original_resource_dict):
        '''
        Tests that inserting a new key (NewKey) results in that new key existing.
        '''
        print("in test" + str(original_resource_dict))
        override_dict = {
            "ParentKey" : {
                ">>NewKey" :{
                    "NewNestedKey" : "NewNestedValue"
                }
            }
        }
        expected_overwritten_dict = {
            "ParentKey" : {
                "OldKey" :{
                    "OldNestedKey" : "OldNestedValue"
                },
                "NewKey" :{
                    "NewNestedKey" : "NewNestedValue"
                }
            }
        }

        assert override_resources(original_resource_dict, override_dict) == expected_overwritten_dict

    def test_override_resource_merge_dicts(self, original_resource_dict):
        '''
        Tests that merging a ParentKey results in ParentKey having the old key (OldKey) and the new key (NewKey)
        '''
        override_dict = {
            "^^ParentKey" : {
                "NewKey" : {
                    "NewNestedKey" : "NewNestedValue"
                }
            }
        }
        expected_overwritten_dict = {
            "ParentKey" : {
                "OldKey" : {
                    "OldNestedKey" : "OldNestedValue"
                },
                "NewKey" : {
                    "NewNestedKey" : "NewNestedValue"
                }
            }
        }

        assert override_resources(original_resource_dict, override_dict) == expected_overwritten_dict

    def test_override_resource_delete_dict(self, original_resource_dict_four_keys):
        '''
        Tests that removing keys (OldKey1, OldKey2, OldKey3, OldKey4) do infact remove the keys from the resource dictionary.
        '''

        override_dict = {
            "ParentKey" : {
                "<<OldKey1" : {},
                "<<OldKey2" : [],
                 "<<OldKey3" : "this shouldnt matter",
                 "<<OldKey4" : None
            }
        }

        expected_overwritten_dict = {
            "ParentKey" : {}
        }

        assert override_resources(original_resource_dict_four_keys, override_dict) == expected_overwritten_dict

    def test_override_resource_new_list_element(self, original_resource_dict_four_elements):
        '''
        Tests that overriding a key (ParentKey) will infact replace it and not merge the old and new values etc
        '''
        override_dict = {
            ">>ParentKey" : [
                {
                "NewKey" :{
                    "NewNestedKey" : "NewNestedValue"
                }
            }
            ]
        }

        expected_overwritten_dict = {
            "ParentKey" : [
                {
                    "NewKey" :{
                        "NewNestedKey" : "NewNestedValue"
                    }
                }
            ]
        }

        assert override_resources(original_resource_dict_four_elements, override_dict) == expected_overwritten_dict


    def test_override_resource_merge_list_element(self, original_resource_dict_four_elements):
        '''
        Tests that merging a key (ParentKey) results in the original child keys (OldKey1, OldKey2, OldKey3, OldKey4)
        and the new key (OldKey5) being in the resource dict.
        '''
        override_dict = {
            "^^ParentKey" : [
                {
                    "OldKey5" :{
                        "OldNestedKey" : "OldNestedValue"
                    }
                }
            ]
        }

        expected_overwritten_dict = {
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
                },
                {
                    "OldKey5" :{
                        "OldNestedKey" : "OldNestedValue"
                    }
                }
            ]
        }
        assert override_resources(original_resource_dict_four_elements, override_dict) == expected_overwritten_dict

    def test_override_resource_errors_when_merging_string_or_int(self, original_resource_dict_string_and_int):
        '''
        It is only possible to merge keys if the values are dicts or lists.
        This tests that an exception is raised when trying to merge keys where their value is a string (String),
        and int (Int) or null (None)
        '''
        override_list = [
            {
                "^^String" : "new string"
            },
            {
                "^^Int" : 456
            },
            {
                "^^None" : None
            }
        ]
        for override_dict in override_list:
            with pytest.raises(Exception):
                override_resources(original_resource_string_and_int, override_dict)