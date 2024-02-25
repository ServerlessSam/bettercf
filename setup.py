# read the contents of your README file
from pathlib import Path

from setuptools import find_packages, setup

from src.bettercf.cli_version import __version__

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="bettercf",
    version=__version__,
    license="MIT",
    author="Samuel Lock",
    author_email="serverlesssam@gmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/ServerlessSam/bettercf",
    keywords="CloudFormation stack management solution",
    description="CloudFormation stack management solution",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
