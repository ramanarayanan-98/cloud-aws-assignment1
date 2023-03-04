import json
import boto3
from boto3.dynamodb.conditions import Key
import requests

class Unstructured:
    def __init__(self,msg):
        self.text = msg

class Message:
    def __init__(self, msgtext):
        self.type = "unstructured"
        self.unstructured = Unstructured(msgtext)
        # self.structured = Unstructured() #Should change this if required

class BotReponse:
    def __init__(self):
        self.messages = []
    
    def appendNewMessage(self,newMessage):
        if not isinstance(newMessage,Message):
            return
        
        self.messages.append(newMessage)
        
def lambda_handler(event, context):
    outputObj = BotReponse()
    for i in range(len(event["messages"])):
        msg = event["messages"][i]["unstructured"]["text"]
        retmsg = Message(processMsg(msg))
        outputObj.appendNewMessage(retmsg)
        

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps(outputObj,default=to_serializable)
    }

def to_serializable(val):
    if hasattr(val, '__dict__'):
        return val.__dict__
    return val
    
def processMsg(msg:str)->str:
    greetings=["hello how are you", "hi", "hello", "good morning", "good afternoon", "good evening"]
    msg = msg.lower()
    dynamodb = boto3.resource('dynamodb',  aws_access_key_id="AKIA4W7FFVFRKSJIONJW", aws_secret_access_key="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",region_name = "us-east-1")
    table = dynamodb.Table('user_restaurant_recommendation_data')
    response = table.query(
            KeyConditionExpression=Key('user_uuid').eq("1234")
        )
    
    if msg in greetings and len(response["Items"])!=0:
        return "Hello, welcome to Ram and Vinayak's chatbot. If you need recommendations based on your previous chat type 'previous'. If you need new suggestions type 'restaurants'."
    
    elif msg =="previous":
        
        user_details = response["Items"][0]["user_details"]
        dynamo_res = response["Items"][0]["restaurants"]

        SENDER = 'diningbotconcierge@gmail.com'
        RECIPIENT = user_details["Email"]
        ses_client = boto3.client('ses', aws_access_key_id="AKIA4W7FFVFRKSJIONJW", aws_secret_access_key="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")
        msg = f'Hello, So you needed suggestions for {user_details["CuisineType"]} restaurants in {user_details["Location"]} :\nEnjoy your meal!'
        msg += f"\nPrevious Recommendations were =>\n"
        msg += f"----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
        msg += f" NUM           NAME                     ADDRESS                              PHONE NUMBER            RATING      REVIEW COUNT\n"
        for i,rest in enumerate(dynamo_res):
            msg += f"  {i+1})  {rest['name']}        {rest['address']}     {rest['phonenum']}        {rest['rating']}          {rest['reviewcnt']}\n"
        msg += f"----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"

        response = ses_client.send_email(
            Destination={
            'ToAddresses': [
                RECIPIENT,
                    ],
            },
            Message={
                'Body': {
                        'Text': {
                        'Charset': 'UTF-8',
                        'Data': msg,
                        },
                    },
                    'Subject': {
                'Charset': 'UTF-8',
                    'Data': 'Chatbot Concierge - Dining Recommendations from Ram and Vinayak',
                },
            },
            Source=SENDER, )
        
        return f"We have sent you the previous recommendations on {user_details['CuisineType']} cuisine to your mail - {user_details['Email']} "

        

    else:
        client = boto3.client('lexv2-runtime', region_name='us-east-1')
        response = client.recognize_text(
            botId='KY2F30BNYR',
            botAliasId='TSTALIASID',
            localeId = 'en_US',
            sessionId ='12345',
            text = msg
        )
        print(response['messages'][0]['content'])
        return response['messages'][0]['content']
    
