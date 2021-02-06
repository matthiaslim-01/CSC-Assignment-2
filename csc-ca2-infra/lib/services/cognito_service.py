import boto3
import logging
from botocore.exceptions import ClientError
from lib.webexception import WebException

def init_client():
    try:
        return boto3.client('cognito-idp', region_name = "us-east-1")
    except ClientError as ce:
        logging.exception("Cognito Identity Failed")
        raise WebException()

def sign_up(username, password):
    cognito = init_client()
    cognito.sign_up(
        ClientId = "2j58pg8b6ltkbkjefbihp3kncs",
        Username = username,
        Password = password
    )