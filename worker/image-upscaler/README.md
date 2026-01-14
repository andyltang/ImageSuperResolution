# Image Upscaling Worker
A scalable worker that consumes messages from SQS to handle user requests asynchronously. Retrieves the original requested image from S3 bucket and upscales them using a pre-trained CNN model to perform inference and produce an upscaled image. Resultant image is uploaded to S3 bucket where the user can request for upscaled version of the image. 

## Requirements
- S3 bucket
- SQS queue
- IAM permissions for S3 and SQS

## Configuration
The service is configured entirely via environment variables.

### Environment Variables

| Variable | Description | Needed for EC2 |
|----------|-------------|----------------|
| `AWS_ACCESS_KEY` | Your AWS Access Key | No |
| `AWS_SECRET_ACCESS_KEY` | Your Secret Access Key | No |
| `AWS_REGION` | AWS region | Yes |
| `AWS_S3_BUCKET` | Target S3 bucket for image uploads | Yes |
| `AWS_SQS_URL` | SQS queue URL | Yes |

## Deployment

### Build Image
```
docker build -t <image_name>:<image_tag> .
```

### Running locally
1. Set the above environment variables
2. Run the image (see start_server script)

### Running on a Linux image
1. Create `/opt/app/.env`:
```
AWS_REGION=your-region
AWS_S3_BUCKET=your-bucket-name
AWS_SQS_URL=https://example.com/1234567890/your-queue
```
2. Run the image passing in env file as an argument (see start_server script)