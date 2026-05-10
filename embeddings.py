import cohere
import os
from dotenv import load_dotenv

load_dotenv()

client = cohere.Client(os.getenv("COHERE_API_KEY"))

def embed(text: str) -> list[float]:
    response = client.embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type="search_document"
    )
    return response.embeddings[0]