import json
import re

import boto3

keyre = re.compile('^AWSAccessKeyId=(.*)$')

def get_keys(file):
    with open(file, 'r') as inf:
        hdr = inf.readline()
        print(hdr)
        # JSON format
        if hdr[0] == '{':
            inf.seek(0)
            return json.load(inf)

        # Root key format
        if keyre.match(hdr):
            out = dict()
            while hdr:
                parts = hdr.split('=')
                out[parts[0]] = parts[1].strip()
                hdr = inf.readline()
            return {
                'aws_access_key_id': out['AWSAccessKeyId'],
                'aws_secret_access_key': out['AWSSecretKey']
            }

        # Colon format
        elif hdr[0] == '#':
            while hdr[0] == '#':
                hdr = inf.readline()
            out = dict()
            while hdr:
                parts = hdr.split(':')
                out[parts[0]] = parts[1].strip()
                hdr = inf.readline()
            return {
                'aws_access_key_id': out['accessKeyId'],
                'aws_secret_access_key': out['secretKey']
            }

        # IAM format
        else:
            keys = inf.readline().split(',')
            return {
                'aws_access_key_id': keys[1].strip(),
                'aws_secret_access_key': keys[2].strip()
            }

# Load credentials
keys = get_keys('credentials.csv')
region = 'us-west-1'
queue_name = 'myqueue'
bucket_name = 'sunrise-pixel-harbor-vault'

if not queue_name: raise Exception('You must set a queue name.')
if not bucket_name: raise Exception('You must set a bucket name.')

# Initialize SQS client
sqs = boto3.client('sqs', region_name=region, **keys)

# Create or get the queue
try:
    response = sqs.create_queue(QueueName=queue_name)
    queue_url = response['QueueUrl']
    print(f"Queue created successfully: {queue_url}")
except sqs.exceptions.QueueNameExists:
    print(f"Queue '{queue_name}' already exists.")

# Initialize S3 client
s3 = boto3.client('s3', region_name=region, **keys)

# Create or get the bucket
try:
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
    print(f"Bucket '{bucket_name}' created successfully.")
except s3.exceptions.BucketAlreadyExists:
    print(f"Bucket '{bucket_name}' already exists.")
