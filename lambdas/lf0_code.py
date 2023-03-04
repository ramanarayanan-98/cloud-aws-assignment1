import json
import boto3

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
    client = boto3.client('lexv2-runtime', region_name='us-east-1')
    response = client.recognize_text(
        botId='<bot-id>',
        botAliasId='<bot-alias-id>',
        localeId = 'en_US',
        sessionId ='12345',
        text = msg
    )
    print(response['messages'][0]['content'])
    return response['messages'][0]['content']
 
