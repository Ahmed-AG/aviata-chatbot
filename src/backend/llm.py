import openai
import os
from weaviate_class import w

def call_llm(query):
    prompt = create_prompt(query)
    openai_response = call_openai(prompt)

    llm_response = {
        "message": openai_response, 
        # "message":"hello", 
        "Your prompt is": query
    }
    return llm_response

def create_prompt(query):
    # get relevant data from VectorDB
    prompt = query
    return prompt

def call_openai(prompt):
    # client = OpenAI()
    openai.api_key = get_openAIKey()

    response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    temperature=0.7,
    messages=[
        {"role": "system", "content": "You are a helpful assistant. And your name is Aviata-chatbot."},
        {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def get_openAIKey():
    return os.getenv('OPENAI_KEY')

