import json
import boto3
import os
from botocore.exceptions import ClientError

dynamodb = boto3.client('dynamodb')
tableName = os.environ["tableName"]


def delete_record(event):
    phoneNumber = event["phoneNumber"]
    try:
        response = dynamodb.delete_item(
            TableName=tableName,
            Key={
                'phoneNumber': {
                    'S': "+852{}".format(phoneNumber)
                }
            }
        )
        return "Delete Successful!"

    except ClientError as e:
        return (e.response['Error']['Message'])
