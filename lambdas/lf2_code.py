import boto3
import json
from boto3.dynamodb.conditions import Key
import requests
from requests_aws4auth import AWS4Auth
import random
import time

def query_elastic_search(cusine):
    awsauth = AWS4Auth("<aws_access_key>", "<aws_secret_access_key>", "<region>", "es")
    host = '<host-url>'
    index = 'restaurant'
    url = host + '/' + index + '/_search?q='+str(cusine)
    
    headers = { "Content-Type": "application/json" }
    r = requests.get(url, auth=awsauth, headers=headers)
    response= r.text
    data = json.loads(response)["hits"]["hits"]
    randomSelectIdx = random.sample(range(0, len(data)-3), 3)
    restaurant_ids = [data[randomSelectIdx[i]]['_source']['id'] for i in range(3)]
    print(f"Elastic Search Result : {data} , Random 3 restaurants : {restaurant_ids}")
    return restaurant_ids

def query_dynamo_table(restaurant_ids):
    dynamodb = boto3.resource('dynamodb',  aws_access_key_id="<aws_access_key>", aws_secret_access_key="<aws_secret_access_key>",region_name = "<region>")
    table = dynamodb.Table('yelp-restaurants-data')
    res = []
    for cur_id in restaurant_ids:
        response = table.query(
            KeyConditionExpression=Key('id').eq(cur_id)
        )
        temp = {}
        temp["name"] = response['Items'][0]['name']
        temp["address"] = response['Items'][0]['location']['display_address']
        temp["phonenum"] = response['Items'][0]['display_phone']
        temp["rating"] = response['Items'][0]['rating']
        temp["reviewcnt"] = response['Items'][0]['review_count']
        res.append(temp)
    print(f"Dynamo Results: {res}")
    return res

def store_user_recommendations_to_dynamo(user_details,restaurant_reco):
    if "user_uuid" not in user_details:
        print(f"Recommendations not saved to Dynamo DB as user_uuid was not passed")
        return
    dynamodb = boto3.resource('dynamodb',  aws_access_key_id="<aws_access_key>", aws_secret_access_key="<aws_secret_access_key>",region_name = "<region>")
    table = dynamodb.Table('user_restaurant_recommendation_data')

    res = {}
    res["user_uuid"] = user_details["user_uuid"]
    res["user_details"] = user_details
    res["restaurants"] = restaurant_reco
    res["insertedAtTimestamp"] = f"{time.time()}"
    table.put_item(Item=res)
    print(f"Recommendations stored to DynamoDB for the user : {user_details['user_uuid']}")

def connect_to_sqs_queue():
    sqs = boto3.client('sqs', aws_access_key_id="<aws_access_key>", aws_secret_access_key="<aws_secret_access_key>")

    QueueUrl = 'https://sqs.us-east-1.amazonaws.com/<queue-id>/messages'

    response = sqs.receive_message(
        QueueUrl=QueueUrl,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    if "Messages" in response and len(response["Messages"]) > 0:
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']
        sqs.delete_message(QueueUrl=QueueUrl, ReceiptHandle=receipt_handle)
    
    return response

def send_email_using_ses(user_details,dynamo_res):
    SENDER = 'diningbotconcierge@gmail.com'
    RECIPIENT = user_details["Email"]
    ses_client = boto3.client('ses', aws_access_key_id="<aws_access_key>", aws_secret_access_key="<aws_secret_access_key>")
    msg = f'Hello, So you needed suggestions for {user_details["CuisineType"]} restaurants in {user_details["Location"]} for {user_details["NumPeople"]} people on {user_details["Date"]} at {user_details["Time"]}:\nEnjoy your meal!'
    msg += f"\nThe recommendations from our side are =>\n"
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
        Source=SENDER,
    )
    return response

def parse_user_details(response):
    user_details = {}
    message = response['Messages'][0]
    user_details["Location"] = message['MessageAttributes']['Location']['StringValue']
    user_details["CuisineType"] = message['MessageAttributes']['CuisineType']['StringValue']
    user_details["Email"] = message['MessageAttributes']['Email']['StringValue']
    user_details["NumPeople"] = message['MessageAttributes']['NumPeople']['StringValue']
    user_details["Date"] = message['MessageAttributes']['Date']['StringValue']
    user_details["Time"] = message['MessageAttributes']['Time']['StringValue']
    print(f"User details are {user_details}")
    return user_details

def lambda_handler(event,context):
    response = connect_to_sqs_queue()

    try:
        user_details = parse_user_details(response)
        restaurant_ids = query_elastic_search(user_details["CuisineType"])
        dynamo_res = query_dynamo_table(restaurant_ids)
        send_email_using_ses(user_details,dynamo_res)
        store_user_recommendations_to_dynamo(user_details,dynamo_res)

    except KeyError:
        return {
            "statusCode":400,
            "body": json.dumps(f"Error : SQS:messages is empty")
            }

    return {
        'statusCode': 200,
        'body': json.dumps(f"Email Successfully sent!")
        }
    



