import json
import boto3
import time
from decimal import Decimal

def lambda_handler(event, context):
    aws_session = boto3.Session()
    client = aws_session.client('s3', region_name="us-east-1")
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-restaurants-data')
    
    files = ["japanese_restaurants.json","mexican_restaurants.json","indian_restaurants.json","italian_restaurants.json","chinese_restaurants.json"]
    
    for jsonfilename in files:
        json_object = client.get_object(Bucket="yelp-restaurants-scraped-data", Key=jsonfilename)
        file_reader = json_object['Body'].read().decode("utf-8")
        file_reader = json.loads(file_reader,parse_float=Decimal)
        
        for item in file_reader:
            item["insertedAtTimestamp"] = f"{time.time()}"
            table.put_item(Item=item)
        
    return "success"
