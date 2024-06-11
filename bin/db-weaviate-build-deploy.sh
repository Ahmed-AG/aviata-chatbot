#!/bin/bash

OPENAI_KEY=$1

cd src/db-weaviate
docker build --build-arg OPENAI_KEY=$OPENAI_KEY -t ahmedag/mo-weaviate .
docker stop mo-weaviate || True
docker run --name mo-weaviate -d --rm -p 9090:8080 mo-weaviate 
cd ../../
docker ps