import boto3, json
from pathlib import Path
from dfm.file_types import JsonFileType
from src.utils import get_latest_version, get_management_bucket_name
from src.version import Version
from dfm.config import BuildConfig
class System():
    name: str
    dfm_config: BuildConfig

    def __init__(
        self,
        system_name:str,
        dfm_config_file_path:Path=Path(__file__).parent.parent.joinpath(".dfm/template_builder.json").resolve(),
        dfm_root_path:Path=Path(__file__).parent.parent.resolve()
    ):
        self.name = system_name
        self.dfm_config = BuildConfig.load_config_from_file(
            file_path = dfm_config_file_path,
            root_path = dfm_root_path,
            parameters = {
                "SystemName" : system_name
            }
        )

    def push(self, version:Version=None, template_str:str=None):

        if not template_str:
            template_str = json.dumps(JsonFileType.load_from_file(self.dfm_config.root_path / self.dfm_config.destination_file.location.substituted_path)).encode('utf-8')
        
        if not version:
            version = Version(System.detect_latest_version(self.name))
            version.auto_increment_version()

        System.push_mechanism(self.name, version, template_str)
        
        return
 
    @staticmethod
    def push_mechanism(name:str, version:Version, template_str:str):
        BUCKET_NAME = get_management_bucket_name()
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Body=template_str,
            Bucket=BUCKET_NAME,
            Key=f"{name}/{version.get_version_string()}"
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
        if "Contents" not in response:
            raise Exception(f"No versions of system: {system_name} detected in management bucket: {BUCKET_NAME}")
        for file in response["Contents"]:
            if file["Key"].split("/")[-1]: #This will be an empty string when s3.list_objects_v2 provides a subfolder instead of an object. Must skip this scenario.
                versions_present.append( #Tuple of major, minor
                    file["Key"].split("/")[-1]
                )
        return get_latest_version(versions_present)
        