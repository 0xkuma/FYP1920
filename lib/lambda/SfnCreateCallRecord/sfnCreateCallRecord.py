import boto3
import json
import os

dynamodb = boto3.client('dynamodb')
tableName = os.environ["tableName"]


def lambda_handler(event, context):
    response = dynamodb.put_item(
        TableName=tableName,
        Item={
            "phoneNumber": {
                "S": event["phoneNumber"]["S"]
            },
            "callTime": {
                "S": event["callTime"]
            },
            "callStatus": {
                "S": "Calling"
            }
        })
    return event
