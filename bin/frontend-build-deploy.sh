#!/bin/bash

BACKEND_URL=$1
echo $BACKEND_URL

cd src/frontend
docker buildx build -f Dockerfile --platform linux/amd64 --build-arg BACKEND_URL=$BACKEND_URL -t ahmedag/frontend .
docker push ahmedag/frontend

# docker stop mo-frontend
# docker run --name mo-frontend -d --rm -p 80:80 mo-frontend 
# docker ps