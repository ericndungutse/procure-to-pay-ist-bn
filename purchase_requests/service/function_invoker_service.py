import boto3
import json
from django.conf import settings

class FunctionEnvokerService:
  @staticmethod
  def envoke_function(function_name, payload):
    lambda_client = boto3.client(
        'lambda',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_KEY
    )
        
    response = lambda_client.invoke(
        FunctionName="FileProcessor",
        InvocationType='Event',
        Payload=json.dumps(payload)
    )
    
    return response['StatusCode']