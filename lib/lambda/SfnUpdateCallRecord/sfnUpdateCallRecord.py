import boto3
import json
import os

dynamodb = boto3.client('dynamodb')
tableName = os.environ["tableName"]


def lambda_handler(event, context):
    print(event)
    body = event
    response = dynamodb.update_item(
        TableName=tableName,
        Key={
            "phoneNumber": {
                "S": body["phoneNumber"]["S"]
            },
            "callTime": {
                "S": body["callTime"]
            }
        },
        UpdateExpression="set callStatus = :t",
        ExpressionAttributeValues={
            ":t": {
                "S": "Timeout"
            }
        })
    return response
