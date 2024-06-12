#!/bin/bash

BACKEND_URL=$1

cd src/frontend
docker buildx build -f Dockerfile --platform linux/amd64 --build-arg BACKEND_URL=$BACKEND_URL -t ahmedag/frontend .
docker push ahmedag/frontend
