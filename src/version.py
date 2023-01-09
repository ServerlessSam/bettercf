import re

class Version():

    def __init__(self, version_string:str):
        try:
            parsed_version = self.major_minor_micro(version_string)
            self.major = parsed_version[0]
            self.minor = parsed_version[1]
            self.micro = parsed_version[2]
        except:
            # Not of maj.min.mic format. Try the other format.
            try:
                parsed_version = self.major_minor(version_string)
                self.major = parsed_version[0]
                self.minor = parsed_version[1]
            except:
                raise Exception(f"Version '{version_string};' is not of the 'X.Y' or 'X.Y.Z' format.")
            
    def major_version_increment(self):
        self.major += 1
        self.minor = 0
        if hasattr(self, "micro"):
            self.micro = 0

    def minor_version_increment(self):
        self.minor += 1
        if hasattr(self, "micro"):
            self.micro = 0

    def micro_version_increment(self):
        self.micro += 1

    def auto_increment_version(self, major_increment:bool=False, micro_increment:bool=False):
        if major_increment and micro_increment:
            raise Exception("Cannot specify a major AND micro version increment at the same time.")

        if micro_increment and not hasattr(self, "micro"):
            raise Exception(f"Attempting to do a micro version increment for a version without a micro")
        if major_increment:
            self.major_version_increment()
        elif micro_increment:
            self.micro_version_increment()
        else:
            self.minor_version_increment()

    #TODO support other versioning syntax? E.g vX.Y?
    def get_version_string(self):
        to_return = [str(self.major), str(self.minor)]
        if hasattr(self, "micro"):
            to_return.append(str(self.micro))
        return ".".join(to_return)

    @staticmethod
    def major_minor_micro(version):
        try:
            major, minor, micro = re.search('^(\d+)\.(\d+)\.(\d+)$', version).groups()
            return int(major), int(minor), int(micro)
        except:
            raise Exception(f"{version} is not a recognizable version.")

    @staticmethod
    def major_minor(version):
        try:
            major, minor = re.search('^(\d+)\.(\d+)$', version).groups()
            return int(major), int(minor)
        except:
            raise Exception(f"{version} is not a recognizable version.")