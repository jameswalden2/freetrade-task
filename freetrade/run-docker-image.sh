#!/bin/bash

IMAGE_NAME="james_walden/freetrade"

echo "build image..."
docker build -t $IMAGE_NAME .

echo "run container..."
CONTAINER_ID=$(docker run -d --env-file .env.freetrade $IMAGE_NAME)

echo "tail logs for container $CONTAINER_ID..."
docker logs -f $CONTAINER_ID