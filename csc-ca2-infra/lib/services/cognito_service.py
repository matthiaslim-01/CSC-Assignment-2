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
        ClientId = "",
        Username = username,
        Password = password
    )

def sign_in(username, password):
    cognito = init_client()