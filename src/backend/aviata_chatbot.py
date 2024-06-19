from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from llm import llm
from weaviatedb import weaviatedb

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
    # allow_credentials=True,
    # allow_methods=["GET", "POST", "PUT", "DELETE"],  # Add other HTTP methods as needed
    # allow_headers=["*"],  # Allow all headers, or specify specific headers
)
# LLM API
@app.get("/api/llm")
def read_root(q: str = None):
    l = llm()
    response = l.call_llm(q)
    return response

@app.get("/api/update-db")
def read_root(class_name: str = "SANS_Cloud_Exchange"):
    w = weaviatedb(class_name=class_name)
    response = w.upload_documents()
    return response


@app.get("/api/hello")
def read_root():
    return {"message": "Hello, World!"}

class Data(BaseModel):
    key: str

@app.post("/api/data")
def receive_data(data: Data):
    return {"received": data}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)