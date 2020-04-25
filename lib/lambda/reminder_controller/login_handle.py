import json
import boto3
import os
import time
from botocore.exceptions import ClientError
from datetime import datetime, timedelta


dynamodb = boto3.client('dynamodb')
tableName = "FypStack-LexStackTelegramUserF5E115A7-1XKCM33IQSDCA"


def login_handle(event):
    body = json.loads(event)
    try:
        response = dynamodb.get_item(
            TableName=tableName,
            Key={
                'TelegramID': {
                    'S': str(body['userId'])
                }
            }
        )
        try:
            return str(response)

        except ClientError as e:
            return (e.response['Error']['Message'])

        except:
            return "Phone Number Not Found"

    except ClientError as e:
        return (e.response['Error']['Message'])
