from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import json
import logging
import os
import boto3
logger = logging.getLogger()
logger.setLevel(logging.INFO)

line_bot_api = LineBotApi(os.getenv('ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('SECRET'))

lex = boto3.client('lex-runtime')


def lambda_handler(event, context):
    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):

        logger.info(event)

        response = lex.post_text(
            botName='ReminderController',
            botAlias='ElderlyHelper',
            userId=event.source.user_id,
            sessionAttributes={"app": "Line"},
            inputText=event.message.text
        )

        logger.info(response)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response["message"]))
    try:
        # get X-Line-Signature header value
        signature = event['headers']['X-Line-Signature']
        # get event body
        body = event['body']
        # handle webhook body
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {'statusCode': 400, 'body': 'InvalidSignature'}
    except Exception as e:
        logger.info(e)
        # return e
    return {'statusCode': 200, 'body': 'OK'}
