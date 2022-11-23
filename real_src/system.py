import boto3, logging, importlib, json
from pathlib import Path
from real_src.file_handling import load_file_to_dict
dfm = importlib.import_module("data-file-merge") #TODO remove this workaroudn when dfm v0.3 is released

class System():
    name: str
    version: str
    
    def push(self, local_file_path:Path):
        BUCKET_NAME = "" #TODO get this from somewhere
        try:
            s3_client = boto3.client('s3')
            s3_client.put_object(
                Body=json.dumps(load_file_to_dict(local_file_path)).encode('utf-8'),
                Bucket=BUCKET_NAME,
                Key=f"{self.name}/{self.version}"
            )
        except boto3.ClientError as e:
            logging.error(e)
        return

    @staticmethod
    def build(system_name:str, file_path_override:Path=None, root_path_override:Path=None):

        # Deal with potential overrides
        file_path = Path(__file__).parent.parent.child(".dfm").child("template_builder.json").resolve()
        if file_path_override:
            file_path = file_path_override
        root_path = Path(__file__).parent.parent.resolve()
        if root_path_override:
            root_path = root_path_override

        system_config = dfm.config.BuildConfig.load_config_from_file(
            file_path = file_path,
            root_path = root_path,
            parameters = {
                "SYSTEM_NAME" : system_name
            }
        )
        system_config.build()
        return