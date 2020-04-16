import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import dateutil.tz
import os

hk_tz = dateutil.tz.gettz('Asia/Hong_Kong')
dynamodb = boto3.client('dynamodb')
sfn = boto3.client('stepfunctions')

MachineArn = os.environ['StepfunctionArn']
tableName = os.environ["tableName"]

def lambda_handler(event, context):
    dateTimeObj = datetime.now(tz=hk_tz)
    dt_object = datetime.timestamp(dateTimeObj)

    response = dynamodb.get_item(
        TableName=tableName,
        AttributesToGet=['device_1', 'phoneNumber'],
        Key={
            "device_1": {
                "S": event["device_1"],
                    }
        }

    )
    # print(response)

    name = '{0:%Y-%m-%d-%H-%M-%S}'.format(dateTimeObj) + "-callout"
    items = response['Item']
    items.update({'choose': "warning"})
    items.update({'callTime': str(int(dt_object))})
    keys = list([items])
    start = sfn.start_execution(
        stateMachineArn=MachineArn,
        name=name,
        input=json.dumps(keys)
    )
    return start