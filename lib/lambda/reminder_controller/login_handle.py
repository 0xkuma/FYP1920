import json
import boto3
import os
import time
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import random


dynamodb = boto3.client('dynamodb')
sns = boto3.client('sns')

def get_table_name(app):
    if app == "Telegram":
        return 'FypStack-LexStackTelegramUserF5E115A7-1JVNF57O2NMO0'
    else:
        return 'FypStack-LexStackLineUserAC127E6D-CXS0NVE5047D'

def isexpired_time(event):
    body = json.loads(event)
    userID = body['userId']
    app = body['app']
    
    try:
        response = dynamodb.get_item(
            TableName=get_table_name(app),
            Key={
                'userID': {
                    'S': str(userID)
                }
            }
        )
        expired_time = datetime.strptime(response['Item']['expiredTime']['S'], '%Y-%m-%d %H:%M:%S.%f')
        now_time = datetime.now()
        return True if now_time >= expired_time else False
        
    except ClientError as e:
        return (e.response['Error']['Message'])


def update_expired_time(userID, tableName):
    new_expired_time = datetime.now() + timedelta(hours=1)
    try:
        response = dynamodb.update_item(
            TableName=tableName,
            Key={
                'userID': {
                    'S': str(userID)
                }
            },
            ExpressionAttributeNames={
                "#T": "expiredTime"
            },
            ExpressionAttributeValues={
                ":time": {
                    'S': str(new_expired_time)
                }
            },
            UpdateExpression="set #T = :time",
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        return (e.response['Error']['Message'])
        
        
def send_one_time_conde(userID, tableName):
    try:
        response = dynamodb.get_item(
            TableName=tableName,
            Key={
                'userID': {
                    'S': str(userID)
                }
            }
        )
        try:
            items = response['Item']
            phoneNumber = items['phoneNumber']['S']
            oneTimeCode = items['oneTimeCode']['S']
            response = sns.publish(
                PhoneNumber=phoneNumber,
                Message='Your One Time Code is {}'.format(oneTimeCode),
                Subject='ElderHelper'
            )
        except ClientError as e:
            return (e.response['Error']['Message'])

    except ClientError as e:
        return (e.response['Error']['Message'])
    
        
def update_one_time_code(event):
    body = json.loads(event)
    userID = body['userId']
    app = body['app']
    tableName = get_table_name(app)
    code = random.randrange(100000, 999999)
    try:
        response = dynamodb.update_item(
            TableName=tableName,
            Key={
                'userID': {
                    'S': str(userID)
                }
            },
            ExpressionAttributeNames={
                "#C": "oneTimeCode"
            },
            ExpressionAttributeValues={
                ":code": {
                    'S': str(code)
                }
            },
            UpdateExpression="set #C = :code",
            ReturnValues="UPDATED_NEW"
        )
        send_one_time_conde(userID, tableName)
    except ClientError as e:
        return (e.response['Error']['Message'])



def login_handle(event):
    body = json.loads(event)
    userID = body['userId']
    oneTimeCode = body['oneTimeCode']
    app = body['app']
    tableName = get_table_name(app)
    
    try:
        response = dynamodb.get_item(
            TableName=tableName,
            Key={
                'userID': {
                    'S': str(userID)
                }
            }
        )
        try:
            items = response['Item']
            check_one_time_code = items['oneTimeCode']['S']
            userID = items['userID']['S']
            if oneTimeCode ==  check_one_time_code:
                update_expired_time(userID, tableName)
                return "Access Success"
            else:
                return "Code Error"
            

        except ClientError as e:
            return (e.response['Error']['Message'])

    except ClientError as e:
        return (e.response['Error']['Message'])
