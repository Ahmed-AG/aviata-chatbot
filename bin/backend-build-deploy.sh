#!/bin/bash

OPENAI_KEY=$1

cd src/backend
docker buildx build -f Dockerfile --platform linux/amd64 --build-arg OPENAI_KEY=$OPENAI_KEY -t ahmedag/backend .
docker push ahmedag/backend
cd ../../
