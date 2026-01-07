"""
Server to handle REST API requests for upscaling images uploaded by users
"""
import json
from pathlib import Path

import uuid
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from PIL import Image
from io import BytesIO
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

p = Path('./configs/aws.json')
with p.open('r', encoding='utf-8') as f:
    config = json.load(f)
queue_url = config['queue_url']
bucket_name = config['bucket_name']

s3_client = boto3.client('s3', region_name=config['region'])
sqs_client = boto3.client('sqs', region_name=config['region'])

dimension = {
    'upscaled': 2
}

def generate_id():
    return str(uuid.uuid4())

def notify_workers(id, scale_factor):
    try:
        message_body = {
            'id': id,
            'scale_factor': scale_factor
        }

        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body)
        )
        print(f"Message sent to SQS: {response['MessageId']}")
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Credentials error: {e}")
    except Exception as e:
        print(f"Failed to send message to SQS: {e}")

def url(name):
    try:
        # get a presigned url to upload to s3
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': name},
            ExpiresIn=3600
        )
        return response
    except Exception as e:
        print(f"Failed to generate URL: {e}")
        return None

# curl -X POST -F "file=@filename.png" http://aws-instance.com/
@app.post("/v1/upload/")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    print('contents read')
    img = Image.open(BytesIO(contents)).convert("RGB")

    id = generate_id()
    key = f'{id}-original'

    # convert image -> bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=buffer,
            ContentType="image/png"
        )
        print(f"Uploaded {key} to S3.")
    except Exception as e:
        print(f"Failed to upload image to S3: {e}")
        return 'upload failed'

    # queue request message to workers to begin processing the resizing
    notify_workers(id, dimension)

    # Return the URLs to the images.
    res = {key: url(f'{id}-{key}') for key in (['original'] + list(dimension.keys()))}
    return res
