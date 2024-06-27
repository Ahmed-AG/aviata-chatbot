from typing import Callable
from pydantic import Field
from langchain.tools.base import BaseTool

from weaviatedb import weaviatedb

# import datetime
# import os.path

# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from google.oauth2 import service_account



class search_vector_db(BaseTool):
    name = "Search Vector DB"
    description = (
        "You can use this to get the relevant information about the SANS Cloud Exchange reports from a vector database"
    )

    def _run(self, query: str) -> str:
        # get relevant data from VectorDB
        w = weaviatedb(class_name="SANS_Cloud_Exchange") #TODO: Make this dynamic
        relevant_documents = w.get_relevant_documents(query)

        response = f"Use this as context: {relevant_documents}.\n{query}"
        return response

    async def _arun(self, query: str) -> str:
        """Use the Cloudwatch tool asynchronously."""
        raise NotImplementedError("Cloudwatch tool does not support async")