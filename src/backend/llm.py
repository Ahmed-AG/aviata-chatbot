import openai
from common import common
from weaviatedb import weaviatedb
from langchain_agents import agent_run

class llm:
    def __init__(self, openai_key=common.get_env("OPENAI_KEY"), model="gpt-3.5-turbo", temperature=0.7):
        self.OPENAI_APIKEY = openai_key
        self.MODEL = model
        self.TEMPERATURE = temperature

    def call_llm(self, query):
        prompt = self.create_prompt(query)
        openai_response = self.call_openai(prompt)

        llm_response = {
            "message": openai_response,
            # "message":"hello",
            "Your prompt is": query
        }
        return llm_response

    def create_prompt(self, query):
        # get relevant data from VectorDB
        w = weaviatedb(class_name="SANS_Cloud_Exchange")
        relevant_documents = w.get_relevant_documents(query)

        prompt = f"Use this as context: {relevant_documents}.\n{query}"
        return str(prompt)

    def call_openai(self, prompt):
        # client = OpenAI()
        openai.api_key = self.OPENAI_APIKEY

        response = openai.chat.completions.create(
        model=self.MODEL,
        temperature=self.TEMPERATURE,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. And your name is Aviata-chatbot."},
            {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def call_langchain(self, query):
        langchain_response = agent_run(query)
        response = {
            "message": langchain_response,
            # "message":"hello",
            "Your prompt is": query
        }
        return response