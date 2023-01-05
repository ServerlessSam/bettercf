import boto3, json
from pathlib import Path
from src.file_handling import load_file_to_dict
from src.utils import get_latest_version, get_management_bucket_name
from src.version import Version
from dfm.config import BuildConfig
class System():
    name: str
    version: Version
    dfm_config: BuildConfig

    def __init__(
        self,
        system_name:str,
        version:Version=None,
        dfm_config_file_path:Path=Path(__file__).parent.parent.joinpath(".dfm/template_builder.json").resolve(),
        dfm_root_path:Path=Path(__file__).parent.parent.resolve()
    ):
        
        self.name = system_name
        if not version:
            self.version = Version(System.detect_latest_version(system_name))
            self.version.auto_increment_version()
        else:
            self.version = version

        self.dfm_config = BuildConfig.load_config_from_file(
            file_path = dfm_config_file_path,
            root_path = dfm_root_path,
            parameters = {
                "SystemName" : system_name
            }
        )

    def push(self, body_str:str=None):
        BUCKET_NAME = get_management_bucket_name()
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Body=body_str if body_str else json.dumps(load_file_to_dict(self.dfm_config.destination_file.location.resolved_paths[0])).encode('utf-8'),
            Bucket=BUCKET_NAME,
            Key=f"{self.name}/{self.version.get_version_string()}"
        )
        return
 
    def build(self):
        return self.dfm_config.build()
    
    @staticmethod
    def detect_latest_version(system_name:str):
        BUCKET_NAME = get_management_bucket_name()
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=f"{system_name}/",
            #ContinuationToken='string' #TODO deal with continuation
        )
        versions_present = []
        for file in response["Contents"]:
            if file["Key"].split("/")[-1]: #This will be an empty string when s3.list_objects_v2 provides a subfolder instead of an object. Must skip this.
                versions_present.append(( #Tuple of major, minor
                    file["Key"].split("/")[-1]
                ))
        return get_latest_version(versions_present)
        