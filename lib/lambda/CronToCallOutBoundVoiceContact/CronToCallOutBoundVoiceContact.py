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


def addValue(item):
    dateTimeObj = datetime.now(tz=hk_tz)
    dt_object = datetime.timestamp(dateTimeObj)
    item.update({'choose': "medicine"})
    item.update({'callTime': str(int(dt_object))})
    return item


def lambda_handler(event, context):
    dateTimeObj = datetime.now(tz=hk_tz)
    dt_object = datetime.timestamp(dateTimeObj)
    response = dynamodb.scan(
        TableName=tableName,
        AttributesToGet=['phoneNumber'],
        ScanFilter={
            'reminderTime': {
                'AttributeValueList': [
                    {
                        'S': str(int(dt_object)),
                    },
                ],
                'ComparisonOperator': 'LE'
            }
        }

    )
    # print(response)
    name = '{0:%Y-%m-%d-%H-%M-%S}'.format(dateTimeObj) + "-callout"
    # items["executionArn"] = MachineArn+":"+name
    items = response['Items']
    keys = list(map(addValue, items))
    response = sfn.start_execution(
        stateMachineArn=MachineArn,
        name=name,
        input=json.dumps(keys)
    )
    print(keys)
