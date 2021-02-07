import logging
import boto3
from time import time
from botocore.exceptions import ClientError
from lib.webexception import WebException


def init_client():
    try:
        return boto3.client("dynamodb", region_name="us-east-1")
    except ClientError as ce:
        logging.exception("DynamoDB Failed")
        raise WebException()


def store_session(session, username):
    db = init_client()
    expiry = int(time()) + 86400
    db.put_item(
        TableName="session-info-dev",
        Item={
            "sessionToken": {"S": session},
            "userID": {"S": username},
            "ttl": {"N": str(expiry)},
        },
    )


def remove_session(session):
    db = init_client()
    db.delete_item(TableName="session-info-dev", Key={"sessionToken": {"S": session}})


def get_session_username(session):
    db = init_client()
    db_result = db.get_item(
        TableName="session-info-dev",
        Key={"sessionToken": {"S": session}},
        ProjectionExpression="userID",
    )
    username = db_result.get("Item", {}).get("userID", {}).get("S", None)
    return username


def get_subscription_plan(username):
    db = init_client()
    db_result = db.get_item(
        TableName="user-info-dev",
        Key={"userID": {"S": username}},
        ProjectionExpression="subscriptionType",
    )
    subscription_type = (
        db_result.get("Item", {}).get("subscriptionType", {}).get("S", "Free")
    )
    return subscription_type == "Paid"


def put_item(username, subscription_plan, last_payment, session):
    db = init_client()
    db.put_item(
        TableName="user-info-dev",
        Item={
            "userID": {"S": username},
            "subscriptionPlan": {"S": subscription_plan},
            "lastPaid": {"S": last_payment},
            "sessionData": {"S": session},
        },
    )


def delete_item(username):
    db = init_client()
    db.delete_item(Key={"userID": {"S": username}})
