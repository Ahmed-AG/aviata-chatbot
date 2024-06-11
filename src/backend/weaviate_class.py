import weaviate
class w:
    def __init__(self, WEAVIATE_URL, OPENAI_APIKEY, CLASS_NAME, NUMBER_OF_RESULTS_TO_RETURN):
        self.OPENAI_APIKEY = OPENAI_APIKEY
        self.CLASS_NAME = CLASS_NAME
        self.NUMBER_OF_RESULTS_TO_RETURN = NUMBER_OF_RESULTS_TO_RETURN
        self.URL = WEAVIATE_URL
    
    def get_relevant_documents(self, QUESTION):
        
        # Connect to Weaviate DB
        client = weaviate.Client(
            url = self.URL,
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
        data = response['data']['Get'][self.CLASS_NAME]
        
        return data
    