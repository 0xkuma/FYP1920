import boto3
import json
from datetime import datetime
import dateutil.tz
import os

hk_tz = dateutil.tz.gettz('Asia/Hong_Kong')
dynamodb = boto3.client('dynamodb')
sfn = boto3.client('stepfunctions')
machineArn = os.environ['StepfunctionArn']
tableName = os.environ["tableName"]


def lambda_handler(event, context):
    print(event)
    for record in event["Records"]:
        type = record["eventName"]
        if type == "MODIFY":
            dateTimeObj = datetime.now(tz=hk_tz)
            dt_object = datetime.timestamp(dateTimeObj)
            phoneNumber = record["dynamodb"]["NewImage"]["phoneNumber"]["S"]
            callTime = record["dynamodb"]["NewImage"]["callTime"]["S"]
            callStatus = record['dynamodb']['NewImage']['callStatus']['S']
            if callStatus == "CompleteCall":
                pass
            else:
                response = dynamodb.get_item(
                    TableName=tableName,
                    AttributesToGet=['phoneNumber', 'urgentNumber'],
                    Key={
                        "phoneNumber": {
                            "S": phoneNumber,
                        }
                    }
                )

                name = '{0:%Y-%m-%d-%H-%M-%S}'.format(dateTimeObj) + "-callout"
                items = response['Item']
                items.update({'choose': "urgent"})
                items.update({'callTime': callTime})
                items.update({'phoneNumber': items["urgentNumber"]})
                keys = list([items])
                start = sfn.start_execution(
                    stateMachineArn=machineArn,
                    name=name,
                    input=json.dumps(keys)
                )
    print('Successfully processed %s records.' % str(len(event['Records'])))
