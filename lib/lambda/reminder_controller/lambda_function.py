import json
import time
import os
import logging
import re

from create_record import *
from read_record import *
from update_record import *
from delete_record import *
from responses_handle import *
from valid_data import *
from login_handle import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def message(msg):
    return {
        "contentType": "PlainText",
        "content": msg
    }


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

# --- Helper Functions ---


def try_ex(func):
    try:
        return func()
    except KeyError:
        return None

# --- Intents ---


def dispatch(intent_request):
    logger.debug('dispatch userId={} intentName={}'.format(
        intent_request['userId'], intent_request['currentIntent']['name']))
    intent_name, slots = (
        intent_request['currentIntent']['name'], get_slots(intent_request))
    confirmation_status = intent_request['currentIntent']['confirmationStatus']
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {
    }
    phoneNumber = try_ex(lambda: slots["phoneNumber"])
    reminderDate = try_ex(lambda: slots["reminderDate"])
    reminderTime = try_ex(lambda: slots["reminderTime"])
    oneTimeCode = try_ex(lambda: slots["oneTimeCode"])

    # Load confirmation history and track the current state.
    chatsession = json.dumps({
        "phoneNumber": phoneNumber,
        "reminderDate": reminderDate,
        "reminderTime": reminderTime,
        "oneTimeCode": oneTimeCode,
        "userId": intent_request['userId'],
        "app": intent_request['sessionAttributes']['app']
    })
    session_attributes['currentState'] = chatsession
    logger.debug('chatsession={}'.format(chatsession))
    
    if intent_name != 'LoginIntent':
        if isexpired_time(chatsession):
            msg = message("Please login!")
            return close(session_attributes, "Failed", msg)

    if intent_name == 'CreateReminder':
        if intent_request['invocationSource'] == 'DialogCodeHook':
            if phoneNumber and not isvalid_phoneNumber(phoneNumber):
                msg = message("The Phone Number is wrong! Please enter again!")
                return elicit_slot(session_attributes, intent_name, slots, "phoneNumber", msg)
            if reminderDate and not isvalid_date(reminderDate):
                msg = message("The Date is wrong! Please enter again!")
                return elicit_slot(session_attributes, intent_name, slots, "reminderDate", msg)
            if reminderTime and not isvalid_time(reminderDate, reminderTime):
                msg = message("The Time is wrong! Please enter again!")
                return elicit_slot(session_attributes, intent_name, slots, "reminderTime", msg)

            if not phoneNumber or not reminderDate or not reminderTime:
                return delegate(session_attributes, slots)

            if confirmation_status == 'None':
                msg = message(
                    "Are you sure the phone number is {}?".format(phoneNumber))
                return confirm_intent(session_attributes, intent_name, slots, msg)
            if confirmation_status == 'Confirmed':
                msg = message(create_record(slots))
                return close(session_attributes, "Fulfilled", msg)
            if confirmation_status == 'Denied':
                msg = message("okay, the search is cancel.")
                return close(session_attributes, "Failed", msg)

    if intent_name == 'ReadReminder':
        if intent_request['invocationSource'] == 'DialogCodeHook':
            if phoneNumber and not isvalid_phoneNumber(phoneNumber):
                msg = message("The Phone Number is wrong! Please enter again!")
                return elicit_slot(session_attributes, intent_name, slots, "phoneNumber", msg)

            if not phoneNumber:
                return delegate(session_attributes, slots)

            if confirmation_status == 'None':
                msg = message(
                    "Are you sure the phone number is {}?".format(phoneNumber))
                return confirm_intent(session_attributes, intent_name, slots, msg)
            if confirmation_status == 'Confirmed':
                msg = message(read_record(slots))
                return close(session_attributes, "Fulfilled", msg)
            if confirmation_status == 'Denied':
                msg = message("okay, the search is cancel.")
                return close(session_attributes, "Failed", msg)

    if intent_name == 'UpdateReminder':
        if intent_request['invocationSource'] == 'DialogCodeHook':
            if phoneNumber and not isvalid_phoneNumber(phoneNumber):
                msg = message("The Phone Number is wrong! Please enter again!")
                return elicit_slot(session_attributes, intent_name, slots, "phoneNumber", msg)
            if phoneNumber and not isexist_phoneNumber(phoneNumber):
                msg = message(
                    "The Phone Number is not exist! Please enter again!")
                return elicit_slot(session_attributes, intent_name, slots, "phoneNumber", msg)
            if reminderDate and not isvalid_date(reminderDate):
                msg = message("The Date is wrong! Please enter again!")
                return elicit_slot(session_attributes, intent_name, slots, "reminderDate", msg)
            if reminderTime and not isvalid_time(reminderDate, reminderTime):
                msg = message("The Time is wrong! Please enter again!")
                return elicit_slot(session_attributes, intent_name, slots, "reminderTime", msg)

            if not phoneNumber or not reminderDate or not reminderTime:
                return delegate(session_attributes, slots)

            if confirmation_status == 'None':
                msg = message(
                    "Are you sure the phone number is {}?".format(phoneNumber))
                return confirm_intent(session_attributes, intent_name, slots, msg)
            if confirmation_status == 'Confirmed':
                msg = message(update_record(slots))
                return close(session_attributes, "Fulfilled", msg)
            if confirmation_status == 'Denied':
                msg = message("okay, the search is cancel.")
                return close(session_attributes, "Failed", msg)

    if intent_name == 'DeleteReminder':
        if intent_request['invocationSource'] == 'DialogCodeHook':
            if phoneNumber and not isvalid_phoneNumber(phoneNumber):
                msg = message("The Phone Number is wrong! Please enter again!")
                return elicit_slot(session_attributes, intent_name, slots, "phoneNumber", msg)
            if phoneNumber and not isexist_phoneNumber(phoneNumber):
                msg = message(
                    "The Phone Number is not exist! Please enter again!")
                return elicit_slot(session_attributes, intent_name, slots, "phoneNumber", msg)

            if not phoneNumber:
                return delegate(session_attributes, slots)

            if confirmation_status == 'None':
                msg = message(
                    "Are you sure the phone number is {}?".format(phoneNumber))
                return confirm_intent(session_attributes, intent_name, slots, msg)
            if confirmation_status == 'Confirmed':
                msg = message(delete_record(slots))
                return close(session_attributes, "Fulfilled", msg)
            if confirmation_status == 'Denied':
                msg = message("okay, the search is cancel.")
                return close(session_attributes, "Failed", msg)

    if intent_name == 'LoginIntent':
        if intent_request['invocationSource'] == 'DialogCodeHook':
            if not oneTimeCode:
                update_one_time_code(chatsession)
                return delegate(session_attributes, slots)

            if confirmation_status == 'None':
                msg = message(
                    "Are you sure the code is {}?".format(oneTimeCode))
                return confirm_intent(session_attributes, intent_name, slots, msg)
            if confirmation_status == 'Confirmed':
                msg = message(login_handle(session_attributes['currentState']))
                return close(session_attributes, "Fulfilled", msg)
            if confirmation_status == 'Denied':
                msg = message("Please enter the code again!")
                return elicit_slot(session_attributes, intent_name, slots, "oneTimeCode", msg)

    raise Exception('Intent with name ' + intent_name + ' not supported')


def lambda_handler(event, context):
    os.environ['TZ'] = 'Asia/Hong_Kong'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    logger.debug('List all={}'.format(event))

    return dispatch(event)