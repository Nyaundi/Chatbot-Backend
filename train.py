import os
import traceback
from pinecone import Pinecone
import os
from database_operation.save2db import *
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np


load_dotenv(".env.local")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_KEY_BILLED = os.getenv("OPENAI_KEY_BILLED")

# pc.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
pc = Pinecone(api_key=PINECONE_API_KEY)
embedding_client = OpenAI(api_key=OPENAI_KEY_BILLED)


def get_embedding(content, pdf_index):
    try:
        # Embed a line of text
        response = embedding_client.embeddings.create(
            input=content,
            # model="text-embedding-ada-002",
            model="text-embedding-3-small",
        )
        embedding = []
        vec_indexes = []
        # Extract the AI output embedding as a list of floats
        # embedding = response["data"][0]["embedding"]
        # Extract embeddings from the response
        embeddings = [data.embedding for data in response.data]
        embeddings_array = np.array(embeddings)
        # Generate vector indexes
        vec_indexes = [f"vec{i}-{pdf_index}" for i, _ in enumerate(embeddings, start=1)]
        # Save the result to a file
        # save_embeddings_to_file(content, embeddings_array, vec_indexes)
        # creating the vector indexes
        return content, embeddings_array, vec_indexes
    except Exception as e:
        print(traceback.format_exc())
        return [], [], []
