import json
import boto3
import requests
import os

lex = boto3.client('lex-runtime')
TELE_TOKEN = os.getenv('TELE_TOKEN')
URL = "https://api.telegram.org/bot{}/".format(TELE_TOKEN)


def message_handler(msg, chat_id):
    response = lex.post_text(
        botName='ReminderController',
        botAlias='ElderlyHelper',
        userId=str(chat_id),
        sessionAttributes={},
        inputText=msg
    )
    return response["message"]


def send_message(msg, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(msg, chat_id)
    requests.get(url)


def lambda_handler(event, context):
    message = json.loads(event['body'])
    chat_id = message['message']['chat']['id']
    msg = message['message']['text']
    send_message(message_handler(msg, chat_id), chat_id)
    return {
        'statusCode': 200
    }
