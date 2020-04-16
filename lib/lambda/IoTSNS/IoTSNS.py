import boto3

sns = boto3.client('sns')


def lambda_handler(event, context):

    response = sns.publish(
        PhoneNumber=event["phoneNumber"]["S"],
        Message='Test'
    )
    event["waitTime"] = "8"
    
    return event