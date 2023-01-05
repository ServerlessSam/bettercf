

class Region():
    full_name:str
    name:str
    code:str

    AWS_REGIONS_MAPPING = [
    ("US East (Ohio)", "us-east-2", "use2"),
    ("US East (N. Virginia)", "us-east-1", "use1"),
    ("US West (N. California)",	"us-west-1", "usw1"),	
    ("US West (Oregon)", "us-west-2", "usw2"),
    ("Africa (Cape Town)", "af-south-1", "afs1"),
    ("Asia Pacific (Hong Kong)", "ap-east-1", "ape1"),
    ("Asia Pacific (Hyderabad)", "ap-south-2", "aps2"),
    ("Asia Pacific (Jakarta)", "ap-southeast-3", "apse3"),
    ("Asia Pacific (Mumbai)", "ap-south-1", "aps1"),
    ("Asia Pacific (Osaka)", "ap-northeast-3", "apne3"),
    ("Asia Pacific (Seoul)", "ap-northeast-2", "apne2"),
    ("Asia Pacific (Singapore)", "ap-southeast-1", "apse1"),
    ("Asia Pacific (Sydney)", "ap-southeast-2", "apse2"),
    ("Asia Pacific (Tokyo)", "ap-northeast-1", "apne1"),
    ("Canada (Central)", "ca-central-1", "cac1"),
    ("Europe (Frankfurt)", "eu-central-1", "euc1"),
    ("Europe (Ireland)", "eu-west-1", "euw1"),
    ("Europe (London)", "eu-west-2", "euw2"),
    ("Europe (Milan)", "eu-south-1", "eus1"),
    ("Europe (Paris)", "eu-west-3", "euw3"),
    ("Europe (Spain)", "eu-south-2", "eus2"),
    ("Europe (Stockholm)", "eu-north-1", "eun1"),
    ("Europe (Zurich)", "eu-central-2", "euc2"),
    ("Middle East (Bahrain)", "me-south-1", "mes1"),
    ("Middle East (UAE)", "me-central-1", "mec1"),
    ("South America (São Paulo)", "sa-east-1", "sae1"),
    ("AWS GovCloud (US-East)", "us-gov-east-1", "usge1"),
    ("AWS GovCloud (US-West)", "us-gov-west-1", "usgw1")
]

    def __init__(self, name:str=None, code:str=None):
        if name and code:
            raise Exception(f"Cannot supply region name and code ({name} and {code}. Please supply just one.")
        if name:
            self.name = name
            for mapping in self.AWS_REGIONS_MAPPING:
                if mapping[1] == name:
                    self.full_name = mapping[0]
                    self.code = mapping[2]
                    return
            raise Exception(f"Region {name} not recognized.")
        elif code:
            self.code = code
            for mapping in self.AWS_REGIONS_MAPPING:
                if mapping[2] == code:
                    self.full_name = mapping[0]
                    self.name = mapping[1]
                    return
            raise Exception(f"Region {code} not recognized.")
        else:
            raise Exception("Must supply either region name or code. Neither supplied.")
