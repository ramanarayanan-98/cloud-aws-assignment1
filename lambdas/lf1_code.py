import json
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

cuisine = ["indian", "japanese", "chinese", "mexican", "italian"]
location =["manhattan", "nyc", "ny", "new york", "brooklyn", "new york city"]

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False
    
def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')
    


def validate_order(slots):
    # Validate BurgerSize
    Location = slots["Location"]
    CuisineType = slots["CuisineType"]
    NumPeople = slots["NumPeople"]
    date = slots["Date"]
    time = slots["Time"]
    Email = slots["Email"]

    if Location is not None and Location['value']['originalValue'].lower() not in location:
        return {
                'isValid': False,
                'invalidSlot': 'Location',
                'message': 'Please select a Location such as {}.'.format(", ".join(location))
            }
    
    if CuisineType is not None and CuisineType['value']['originalValue'].lower() not in cuisine:
        return {
                'isValid': False,
                'invalidSlot': 'CuisineType',
                'message': 'We currently do not provide this cuisine, would you like to choose from {}? '
                                       .format(", ".join(cuisine))
            }
    
    if NumPeople is not None and (int(NumPeople['value']['originalValue']) < 1):
        return {
                'isValid': False,
                'invalidSlot': 'NumPeople',
                'message': 'The minimum number of people is 1. How many people do you have?'
            }

    return {'isValid': True}


def lambda_handler(event, context):
    print(event)

    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    bot = event['bot']['name']
    intent = event['sessionState']['intent']['name']
    slots = event['sessionState']['intent']['slots']
    print(bot)

    Location = slots["Location"]
    CuisineType = slots["CuisineType"]
    NumPeople = slots["NumPeople"]
    date = slots["Date"]
    Time = slots["Time"]
    Email = slots["Email"]


    order_validation_result = validate_order(slots)

    if event['invocationSource'] == 'DialogCodeHook':
        if not order_validation_result['isValid']:
            if 'message' in order_validation_result:
                response = {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": order_validation_result['invalidSlot'],
                            "type": "ElicitSlot"
                        },
                        "intent": {
                            "name": intent,
                            "slots": slots
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": order_validation_result['message']
                        }
                    ]
                }
            else:
                response = {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": order_validation_result['invalidSlot'],
                            "type": "ElicitSlot"
                        },
                        "intent": {
                            "name": intent,
                            "slots": slots
                        }
                    }
                }
        else:
            response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "Delegate"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots
                    }
                }
            }

    if event['invocationSource'] == 'FulfillmentCodeHook':

        sqs = boto3.client('sqs', aws_access_key_id="<aws_access_key>", aws_secret_access_key="<aws_secret_access_key>")
        # response = sqs.get_queue_url(QueueName='messages')
        # queue_url = response['QueueUrl']
        queue_url = 'https://sqs.us-east-1.amazonaws.com/<queueid>/messages'
        
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageAttributes={
                'Location': {
                'DataType': 'String',
                'StringValue': Location['value']['originalValue']
                },
                'CuisineType': {
                'DataType': 'String',
                'StringValue': CuisineType['value']['originalValue']
                },
                'Date': {
                'DataType': 'String',
                'StringValue': date['value']['originalValue']
                },
                'Time': {
                'DataType': 'String',
                'StringValue': Time['value']['originalValue']
                },
                'NumPeople': {
                'DataType': 'Number',
                'StringValue': str(NumPeople['value']['originalValue'])
                },
                'Email': {
                'DataType': 'String',
                'StringValue': str(Email['value']['originalValue'])
                }
            },
            MessageBody=(
                'Customer details for restaurant reservation'
            )
        )
        
        print('The message id for the response msg is {}'.format(response['MessageId']))
        response = {
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                },
                "intent": {
                    "name": intent,
                    "slots": slots,
                    "state": "Fulfilled"
                }

            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": 'You will receive the suggestions to {}'.format(str(Email['value']['originalValue']))
                }
            ]
        }

    print(response)
    return response