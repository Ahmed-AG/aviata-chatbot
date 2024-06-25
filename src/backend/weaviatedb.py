import weaviate

from common import common
from split_documents import split_documents as sd

class weaviatedb:
    def __init__(self, weaviate_rul=common.get_env("DB_URL"), openai_key=common.get_env("OPENAI_KEY"), class_name="default", number_of_results_to_return=5):
        self.OPENAI_APIKEY = openai_key
        self.CLASS_NAME = class_name
        self.NUMBER_OF_RESULTS_TO_RETURN = number_of_results_to_return
        self.DB_URL = weaviate_rul

    def get_relevant_documents(self, QUESTION):

        # Connect to Weaviate DB
        client = weaviate.Client(
            url = self.DB_URL,
            additional_headers = {
                "X-OpenAI-Api-Key": self.OPENAI_APIKEY
            }
        )

        response = (
            client.query
            .get(self.CLASS_NAME, ["title", "data", "source"])
            .with_near_text({"concepts": QUESTION})
            .with_limit(self.NUMBER_OF_RESULTS_TO_RETURN)
            .do()
        )
        # print(response)
        data = response['data']['Get'][self.CLASS_NAME]

        return data

    def upload_documents(self, SOURCE_DOCUMENTS="data/", CHUNK_SIZE=300, OVERLAP_SIZE=25):
        # TODO: variablize SOURCE_DOCUMENTS
        SOURCE_DOCUMENTS = [
            "data/SANS_Cloud_Exchange_2022_ebook.txt",
            "data/SANS_Cloud_Exchange_2023_ebook.txt"
        ]

        # Connect to Weaviate DB
        client = weaviate.Client(
            # url = "http://localhost:8080",
            url = self.DB_URL,
            additional_headers = {
                "X-OpenAI-Api-Key": self.OPENAI_APIKEY
            }
        )
        class_obj = {
            "class": self.CLASS_NAME,
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
            # print(self.CLASS_NAME)
            # print(class_name['class'])
            if class_name['class'] == self.CLASS_NAME:
                CLASS_EXISTS = True
                break

        # Create class
        if (CLASS_EXISTS == True):
            print(f"Class \"{self.CLASS_NAME}\" exists!")
        else:
            client.schema.create_class(class_obj)
            print(f"Class \"{self.CLASS_NAME}\" Created!")

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
                    class_name=self.CLASS_NAME
                )
        # TODO: Add error handling
        return f"Upload {self.CLASS_NAME} complete!"