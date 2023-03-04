Cloud Computing Assignment 1

Frontend URL : http://diningchatbothw1.com.s3-website-us-east-1.amazonaws.com/

Architecture : 
Frontend <-> API Gateway <-> Lambda Function 0 <-> Lex <-> Lambda Function 1 -> SQS -> Lambda Function 2 -> SES
                                                                                             ^
                                                                                             |
                                                                                    Yelp API -> Elastic Search and DynamoDB