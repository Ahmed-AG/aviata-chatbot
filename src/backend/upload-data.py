# Legacy
# Reference: https://weaviate.io/developers/weaviate/quickstart
import weaviate
import json
import os
import requests
import codecs
from split_documents import split_documents as sd

# Parameters:
OPENAI_APIKEY = os.environ['OPENAI_KEY']
DB_URL = os.environ['DB_URL']
CLASS_NAME = "SANS_Cloud_Exchange"
CHUNK_SIZE = 300
OVERLAP_SIZE = 25
SOURCE_DOCUMENTS = [
    "data/SANS_Cloud_Exchange_2022_ebook.txt",
    "data/SANS_Cloud_Exchange_2023_ebook.txt"
]

# Connect to Weaviate DB
client = weaviate.Client(
    # url = "http://localhost:8080",  
    url = DB_URL,  
    additional_headers = {
        "X-OpenAI-Api-Key": OPENAI_APIKEY  
    }
)

class_obj = {
    "class": CLASS_NAME,
    "vectorizer": "text2vec-openai",  
    "moduleConfig": {
        "text2vec-openai": {},
        "generative-openai": {}
    }
}

# Check Class exists
schema = client.schema.get()
CLASS_EXISTS = False
for class_name in schema['classes']:
    print(CLASS_NAME)
    print(class_name['class'])
    if class_name['class'] == CLASS_NAME:
        CLASS_EXISTS = True
        break

# Create class
if (CLASS_EXISTS == True):
    print("Class esists!")
else:
    client.schema.create_class(class_obj)
    print("Class Created!")

split_documents_data = sd(SOURCE_DOCUMENTS,CHUNK_SIZE , OVERLAP_SIZE)

# Load  Data
client.batch.configure(batch_size=100)
with client.batch as batch:
    for i, d in enumerate(split_documents_data):
        print(f"importing Data: {i+1}: {d['title']}")

        properties = {
            "title": d["title"],
            "data": d["data"],
            "source": d["source"],
        }
        batch.add_data_object(
            data_object=properties,
            class_name=CLASS_NAME
        )