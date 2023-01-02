import os
import sys

from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.skill_builder import CustomSkillBuilder
from boto3.session import Session

# we need this to get ask_local_debug to work
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from .config import AWS_REGION

USL_BASE_URL = os.getenv("apiBaseUrl", "")
aws_session = Session(region_name=AWS_REGION)

sb = CustomSkillBuilder(api_client=DefaultApiClient())
handler = sb.lambda_handler()
