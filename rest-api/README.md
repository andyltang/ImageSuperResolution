# REST API for Image Uploads
A containerized FastAPI web service written in Python that provides a REST endpoint for uploading images. Uploaded images are stored in Amazon S3 and a message is dispatched to Amazon SQS for downstream processing.

## Requirements
- S3 bucket
- SQS queue
- IAM permissions for S3 and SQS

## Configuration
The service is configured entirely via environment variables.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `AWS_REGION` | AWS region |
| `AWS_S3_BUCKET` | Target S3 bucket for image uploads |
| `AWS_SQS_URL` | SQS queue URL |

## Running locally
1. Set the above environment variables
2. Run the image (see start_server script)

## Running on EC2
1. Create `/opt/app/.env`:
```
AWS_REGION=your-region
AWS_S3_BUCKET=your-bucket-name
AWS_SQS_URL=https://example.com/1234567890/your-queue
```
2. Run the image passing in as an argument (see start_server script)