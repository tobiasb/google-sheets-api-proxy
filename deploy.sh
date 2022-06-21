#!/bin/bash

set -ex

CONTAINER_NAME=google-sheets-api-proxy

docker rm -f "$CONTAINER_NAME"
docker build -t google-sheets-api-proxy .

docker run --env-file=.env \
           --publish=5001:5000 \
           --detach \
           --restart=unless-stopped \
           --name "$CONTAINER_NAME" \
           google-sheets-api-proxy
