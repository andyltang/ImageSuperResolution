"""
Scalable worker that polls for messages in SQS
Upscales images using Pytorch trained CNN model and uploads upscaled images to S3 bucket
"""
import os
import json
import io
import uuid
import torch
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from PIL import Image
from lesrcnn import load
from image_upscaler import upscale

REGION = os.environ["AWS_REGION"]
S3_BUCKET = os.environ["AWS_S3_BUCKET"]
SQS_URL = os.environ["AWS_SQS_URL"]
sqs_client = boto3.client('sqs', region_name=REGION)
s3_client = boto3.client('s3', region_name=REGION)

dimension = {
    'upscaled': 2
}

def generate_id():
    return str(uuid.uuid4())

def read_from_s3(key):
    response = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
    image_data = response['Body'].read()
    return Image.open(io.BytesIO(image_data))

def write_to_s3(key, image, format='PNG'):
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    s3_client.put_object(Bucket=S3_BUCKET, Key=key, Body=buffer, ContentType=f'image/{format.lower()}')

def process_image(image, model):
    return upscale(image, model)

def process_image_message(body, receiptHandle, model):
    image_id = body['id']
    scale_factor = body['scale_factor']

    original_key = f'{image_id}-original'
    print('Reading original file')
    image = read_from_s3(original_key)

    result_key = f'{image_id}-upscaled'
    print('Upscaling image')
    try:
        result_image = process_image(image, model)
    except Exception as e:
        print(f"Error processing image: {e}")
    
    print('Writing to s3')
    write_to_s3(result_key, result_image)

    print('Deleting message')
    sqs_client.delete_message(
        QueueUrl=SQS_URL,
        ReceiptHandle=receiptHandle
    )


def main():
    model = load()
    print('Worker initialized!')

    while True:
        print('Checking queue for messages...')
        response = sqs_client.receive_message(
            QueueUrl=SQS_URL,
            AttributeNames=['All'],
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )

        messages = response.get('Messages', [])
        if messages:
            for message in messages:
                try:
                    body = json.loads(message['Body'])        
                    print(f"Processing message id={body['id']}")
                    process_image_message(body, message['ReceiptHandle'], model)
                    print(f"Message id={body['id']} finished processing!")
                except Exception as e:
                    print(f"Error processing message id={body['id']}: {e}")
                    sqs_client.delete_message(
                        QueueUrl=SQS_URL,
                        ReceiptHandle=message['ReceiptHandle']
                    )

if __name__ == '__main__':
    print('Worker warming up...')
    main()
