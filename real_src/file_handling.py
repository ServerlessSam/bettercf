import json

def load_file_to_dict(file_path:str):
    with open(file_path, "r") as loadedFile:
        dictionary = json.load(loadedFile)
    return dictionary

def write_dict_to_file(dictionary:dict, output_file_path:str):
    with open(output_file_path, 'w') as output:
        json.dump(dictionary, output, indent=4)