import json
import boto3
import os
import time
from botocore.exceptions import ClientError

dynamodb = boto3.client('dynamodb')
tableName = os.environ["tableName"]


def update_record(event):
    phoneNumber, reminderDate, reminderTime = (
        event["phoneNumber"], event["reminderDate"], event["reminderTime"])
    t = '{} {}'.format(reminderDate, reminderTime)
    obj = time.strptime(t, "%Y-%m-%d %H:%M")
    formatedTime = int(time.mktime(obj))
    try:
        response = dynamodb.update_item(
            TableName=tableName,
            Key={
                'phoneNumber': {
                    'S': "+852{}".format(phoneNumber)
                }
            },
            ExpressionAttributeNames={
                "#T": "reminderTime"
            },
            ExpressionAttributeValues={
                ":time": {
                    'S': str(formatedTime)
                }
            },
            UpdateExpression="set #T = :time",
            ReturnValues="UPDATED_NEW"
        )
        return "Update Successful!"
    except ClientError as e:
        return (e.response['Error']['Message'])
