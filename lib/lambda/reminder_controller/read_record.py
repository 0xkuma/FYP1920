import json
import boto3
import os
import time
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


dynamodb = boto3.client('dynamodb')
tableName = os.environ["tableName"]


def read_record(event):
    phoneNumber = event["phoneNumber"]
    try:
        response = dynamodb.get_item(
            TableName=tableName,
            Key={
                'phoneNumber': {
                    'S': "+852{}".format(phoneNumber)
                }
            }
        )
        try:
            getTime = int(response["Item"]["reminderTime"]["S"])
            msg = time.strftime("%a, %d %B %Y, %R", time.localtime(getTime))
            return "The time is {}".format(msg)

        except ClientError as e:
            return (e.response['Error']['Message'])

        except:
            return "Phone Number Not Found"

    except ClientError as e:
        return (e.response['Error']['Message'])
