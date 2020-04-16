import json
import boto3
import os
from datetime import datetime
import dateutil.tz
dynamodb = boto3.client('dynamodb')
tableName = os.environ["tableName"]
hk_tz = dateutil.tz.gettz('Asia/Hong_Kong')


def lambda_handler(event, context):
    dateTimeObj = datetime.now(tz=hk_tz)
    dt_object = datetime.timestamp(dateTimeObj)
    body = event["Details"]["ContactData"]["Attributes"]
    del body["connectInvoke_arn"]
    del body["send_task_success_arn"]
    del body["taskToken"]
    body["status"] = "Complete Call"
    response = dynamodb.update_item(
        TableName=tableName,
        Key={
            "phoneNumber": {
                "S": body["phoneNumber"]
            },
            "callTime": {
                "S": body["callTime"]
            }
        },
        UpdateExpression="set callStatus = :t",
        ExpressionAttributeValues={
            ":t": {
                "S": body["status"]
            }
        }
    )
