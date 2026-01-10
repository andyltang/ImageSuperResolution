FROM python:3.11-slim
WORKDIR /app

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# install python deps first for caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY . .

# run application
CMD ["python", "worker.py"]
