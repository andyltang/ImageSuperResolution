# React-based Image Uploader
The front-end to the web app that allows users to upload images to be upscaled. This project uses React with Vite for local development and production builds. For deployment, the application is built into static files using Vite, packaged into a Docker image, and served by a Nginx web server.

## Development (local)
npm install
npm run dev

## Build (Docker image)
docker build -t <image_name>:<tag> .

## Run/Deploy
docker run --rm -p <host_port>:<container_port> <image_name>:<tag>