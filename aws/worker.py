import json
from pathlib import Path
import io
import uuid
import torch
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from PIL import Image
from lesrcnn import load
from image_upscaler import upscale

p = Path('./secrets/aws.json')
with p.open('r', encoding='utf-8') as f:
    aws_endpoints = json.load(f)
queue_url = aws_endpoints['queue_url']
bucket_name = aws_endpoints['bucket_name']

sqs = boto3.client('sqs')
s3 = boto3.client('s3')

dimension = {
    'upscaled': 2
}

def generate_id():
    return str(uuid.uuid4())

def read_from_s3(key):
    response = s3.get_object(Bucket=bucket_name, Key=key)
    image_data = response['Body'].read()
    return Image.open(io.BytesIO(image_data))

def write_to_s3(key, image, format='PNG'):
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    s3.put_object(Bucket=bucket_name, Key=key, Body=buffer, ContentType=f'image/{format.lower()}')

def process_image(image, model):
    return upscale(image, model)

def process_image_message(body, receiptHandle, model):
    image_id = body['id']
    scale_factor = body['scale_factor']

    original_key = f'{image_id}-original'
    image = read_from_s3(original_key)

    result_key = f'{image_id}-{'upscaled'}'
    result_image = process_image(image, model)
    write_to_s3(result_key, result_image)

    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receiptHandle
    )


def main():
    model = load()

    while True:
        print('Checking queue for messages...')
        response = sqs.receive_message(
            QueueUrl=queue_url,
            AttributeNames=['All'],
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )

        messages = response.get('Messages', [])
        if messages:
            for message in messages:
                try:
                    body = json.loads(message['Body'])        
                    print(f'Processing message id={body['id']}')
                    process_image_message(body, message['ReceiptHandle'], model)
                    print(f'Message id={body['id']} finished processing!')
                except Exception as e:
                    print(f"Error processing message id={body['id']}: {e}")
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )

if __name__ == '__main__':
    main()
