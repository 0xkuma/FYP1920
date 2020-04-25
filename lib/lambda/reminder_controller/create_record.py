import json
import boto3
import os
import time

dynamodb = boto3.client('dynamodb')
tableName = os.environ["tableName"]


def create_record(event):
    phoneNumber, reminderDate, reminderTime = (
        event["phoneNumber"], event["reminderDate"], event["reminderTime"])
    t = '{} {}'.format(reminderDate, reminderTime)
    obj = time.strptime(t, "%Y-%m-%d %H:%M")
    formatedTime = int(time.mktime(obj))
    try:
        response = dynamodb.put_item(
            TableName=tableName,
            Item={
                'phoneNumber': {
                    'S': "+852{}".format(phoneNumber)
                },
                'reminderTime': {
                    'S': str(formatedTime)
                }
            }
        )
        return "Record is added"
    except:
        return "Add record fail, Please try again."
