# from typing import Callable
# from pydantic import Field
from typing import Callable
from pydantic import Field
from langchain.tools.base import BaseTool
# import .common
import datetime
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

class openai_raw:
    def __init__(self, openai_key=os.getenv("OPENAI_KEY"), model="gpt-3.5-turbo", temperature=0.7):
        self.OPENAI_APIKEY = openai_key
        self.MODEL = model
        self.TEMPERATURE = temperature

    def call_openai(self, prompt):
        openai.api_key = self.OPENAI_APIKEY

        response = openai.chat.completions.create(
        model=self.MODEL,
        temperature=self.TEMPERATURE,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

class custom_openai(BaseTool):
    name = "openai_raw"
    description = (
        "You can use this to summerize existing results or to understand existing results or to asnwer the final question after you have results"
    )

    def _run(self, query: str) -> str:
        assistant = openai_raw()
        response = assistant.call_openai(query)

        return response

    # async def _arun(self, query: str) -> str:
    #     """Use the Cloudwatch tool asynchronously."""
    #     raise NotImplementedError("Cloudwatch tool does not support async")