# AI Image Upscaling Pipeline
This project implements an AI-based image upscaling pipeline using a lightweight convolutional neural network for image super-resolution.

The system is designed as an asynchronous, scalable pipeline:
1. Images are uploaded by users via an REST API endpoint
2. Requests are queued for processing to decouple ingestion from compute
3. Scalable worker processes load a trained PyTorch super-resolution model and perform inference
4. Upscaled images are stored to an object store for retrieval

The architecture separates request handling, model inference, and storage, allowing the pipeline to scale horizontally and handle variable workloads without blocking user requests.

![Diagram of end-to-end dataflow](/dataflow.png)

#### TODO
- Handle failures and implement retry mechanisms
- Split the responsibilities of the API server further into uploader service