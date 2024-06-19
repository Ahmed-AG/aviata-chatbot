from llm import llm
from weaviatedb import weaviatedb

# Driver for llm Class
def llm_driver():
    l = llm()
    # print(llm_object.OPENAI_APIKEY)
    response = l.call_llm("tell me about cloud security?")
    print(response)

# Driver for weaviate class
def weaviate_driver():
    w = weaviatedb(class_name="SANS_Cloud_Exchange")
    # print(w.DB_URL)
    print(w.NUMBER_OF_RESULTS_TO_RETURN)
    # print(w.OPENAI_APIKEY)
    # print(w.CLASS_NAME)

    # w.upload_documents()

    response = w.get_relevant_documents("tell me about cloud security")
    print(response)

# Main

llm_driver()
# weaviate_driver()
