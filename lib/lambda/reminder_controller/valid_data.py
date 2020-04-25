import re
import os
from datetime import datetime
import time
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.client('dynamodb')
tableName = os.environ["tableName"]


def isvalid_phoneNumber(phoneNumber):
    return True if re.search("(^[2,3,5,6,9])([0-9]{7}$)", phoneNumber) else False


def isvalid_date(reminderDate):
    print(reminderDate)
    todayDate = datetime.today().strftime("%Y-%m-%d")
    print(todayDate)
    return True if reminderDate >= todayDate else False


def isvalid_time(reminderDate, reminderTime):
    currentTime = int(time.time())
    t = '{} {}'.format(reminderDate, reminderTime)
    obj = time.strptime(t, "%Y-%m-%d %H:%M")
    formatedTime = int(time.mktime(obj))
    return True if formatedTime > currentTime else False


def isexist_phoneNumber(phoneNumber):
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
            result = int(response["Item"]["phoneNumber"]["S"])
            return True
        except:
            return False
    except ClientError as e:
        return False
