import json
import boto3
import os

connect = boto3.client('connect')
sqs = boto3.client('sqs')
sfn = boto3.client('stepfunctions')
send_task_success_arn = os.environ['send_task_success_arn']
connectInvoke_arn = os.environ['connectInvoke_arn']


def lambda_handler(event, context):
    try:
        body = json.loads(event["Records"][0]["body"])
        task_token = body["TaskToken"]
        receiver = body['Message']
        receiver['taskToken'] = task_token
        receiver['status'] = "DropCall"
        receiver['response_intent'] = "null"
        response = connect.start_outbound_voice_contact(
            DestinationPhoneNumber=receiver['phoneNumber']['S'],
            ContactFlowId='a04d7249-f1d5-4bee-9d0f-191f2eef6bee',
            InstanceId='a142f0e1-2d80-4b8b-9efd-d2053580963b',
            SourcePhoneNumber='+18664247993',
            Attributes={
                "taskToken": receiver["taskToken"],
                "status": receiver["status"],
                "response_intent": receiver["response_intent"],
                "send_task_success_arn": send_task_success_arn,
                "connectInvoke_arn": connectInvoke_arn,
                "phoneNumber": receiver["phoneNumber"]['S'],
                "callTime": receiver["callTime"],
                "choose": receiver["choose"]

            }
        )
        return event
    except Exception as err:
        print(err)
        return event
