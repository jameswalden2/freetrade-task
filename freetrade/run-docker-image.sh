#!/bin/bash

IMAGE_NAME="my-docker-image"

echo "Building Docker image..."
docker build -t $IMAGE_NAME .

echo "Running Docker container..."
CONTAINER_ID=$(docker run -d --env-file .env.freetrade $IMAGE_NAME)

echo "Tailing logs for container $CONTAINER_ID..."
docker logs -f $CONTAINER_ID