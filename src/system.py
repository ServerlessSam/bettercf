import boto3, logging, importlib, json
from pathlib import Path
from src.file_handling import load_file_to_dict
from src.utils import get_latest_version
from src.version import Version
dfm = importlib.import_module("data-file-merge") #TODO remove this workaroudn when dfm v0.3 is released

class System():
    name: str
    version: Version
    dfm_config: dfm.config.BuildConfig

    def __init__(self, system_name:str, version:str=None, dfm_config_file_path:Path=Path(__file__).parent.parent.child(".dfm").child("template_builder.json").resolve(), dfm_root_path:Path=Path(__file__).parent.parent.resolve()):
        self.name = system_name
        self.version = Version(version) if version else Version(System.detect_latest_version(system_name)).auto_increment_version()
        self.dfm_config = dfm.config.BuildConfig.load_config_from_file(
            file_path = dfm_config_file_path,
            root_path = dfm_root_path,
            parameters = {
                "SYSTEM_NAME" : system_name
            }
        )

    def push(self):
        BUCKET_NAME = "" #TODO get this from somewhere
        try:
            s3_client = boto3.client('s3')
            s3_client.put_object(
                Body=json.dumps(load_file_to_dict(self.dfm_config.destination_file.destination_file_location.resolved_paths[0])).encode('utf-8'),
                Bucket=BUCKET_NAME,
                Key=f"{self.name}/{self.version}"
            )
        except boto3.ClientError as e:
            logging.error(e)
        return

    def build(self):
        self.dfm_config.build()
    
    @staticmethod
    def detect_latest_version(system_name:str):
        BUCKET_NAME = ""
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix={system_name},
            #ContinuationToken='string' #TODO deal with continuation
        )
        versions_present = []
        for file in response["Contents"]:
            versions_present.append(( #Tuple of major, minor
                file["Key"].split("/")[-1]
            ))
        return get_latest_version(versions_present)
        