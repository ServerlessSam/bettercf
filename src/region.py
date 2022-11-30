

class Region():
    name:str
    code:str

    AWS_REGIONS_MAPPING = [
    ("US East (Ohio)", "us-east-2"),
    ("US East (N. Virginia)", "us-east-1"),
    ("US West (N. California)",	"us-west-1"),	
    ("US West (Oregon)", "us-west-2"),
    ("Africa (Cape Town)", "af-south-1"),
    ("Asia Pacific (Hong Kong)", "ap-east-1"),
    ("Asia Pacific (Hyderabad)", "ap-south-2"),
    ("Asia Pacific (Jakarta)", "ap-southeast-3"),
    ("Asia Pacific (Mumbai)", "ap-south-1"),
    ("Asia Pacific (Osaka)", "ap-northeast-3"),
    ("Asia Pacific (Seoul)", "ap-northeast-2"),
    ("Asia Pacific (Singapore)", "ap-southeast-1"),
    ("Asia Pacific (Sydney)", "ap-southeast-2"),
    ("Asia Pacific (Tokyo)", "ap-northeast-1"),
    ("Canada (Central)", "ca-central-1"),
    ("Europe (Frankfurt)", "eu-central-1"),
    ("Europe (Ireland)", "eu-west-1"),
    ("Europe (London)", "eu-west-2"),
    ("Europe (Milan)", "eu-south-1"),
    ("Europe (Paris)", "eu-west-3"),
    ("Europe (Spain)", "eu-south-2"),
    ("Europe (Stockholm)", "eu-north-1"),
    ("Europe (Zurich)", "eu-central-2"),
    ("Middle East (Bahrain)", "me-south-1"),
    ("Middle East (UAE)", "me-central-1"),
    ("South America (São Paulo)", "sa-east-1"),
    ("AWS GovCloud (US-East)", "us-gov-east-1"),
    ("AWS GovCloud (US-West)", "us-gov-west-1")
]

    def __init__(self, code:str):
        self.code = code
        for mapping in self.AWS_REGIONS_MAPPING:
            if mapping[1] == code:
                self.name = mapping[0]
                break
