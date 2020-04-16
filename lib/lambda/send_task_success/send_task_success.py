import os
import datetime
import json
import sys
import boto3

stepfunctions_client = boto3.client("stepfunctions")


def lambda_handler(event, context):
    print(event)

    taskToken = event["Details"]["ContactData"]["Attributes"]["taskToken"]
    message = event["Details"]["ContactData"]["Attributes"]
    message["phoneNumber"] = event["Details"]["ContactData"]["Attributes"]["phoneNumber"]
    message["callTime"] = event["Details"]["ContactData"]["Attributes"]["callTime"]
    del message["taskToken"]
    del message["connectInvoke_arn"]
    del message["send_task_success_arn"]

    message["status"] = "CallCompleted"
    stepfunctions_client.send_task_success(taskToken=taskToken,
                                           output=json.dumps(message))
    print(message)
    return message
