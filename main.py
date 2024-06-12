from flask import Flask, request, jsonify
from waitress import serve

# from langchain_community.llms import openai
# from openai import OpenAI
from openai import OpenAI
import traceback
from pinecone import Pinecone
from flask_cors import CORS
from flask import Flask, send_from_directory
from langchain.prompts.prompt import PromptTemplate
from dotenv import load_dotenv
import os

from proxy_rotation import get_next_proxy, set_proxy_env
from train import get_embedding

load_dotenv(".env.local")

app = Flask(__name__, static_folder="../chatpdf/build/static")
CORS(app)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
OPENAI_KEY = os.getenv("OPENAI_KEY_BILLED")
client = OpenAI(api_key=OPENAI_KEY)


UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# Enable debug mode
app.config["DEBUG"] = True

pc = Pinecone(api_key=PINECONE_API_KEY)
activate_indexs = pc.list_indexes()
PINECONE_INDEX = pc.Index(activate_indexs[0]["name"])


@app.route("/")
def index():
    return send_from_directory("/build", "index.html")


@app.route("/<path:text>")
def all_routes(text):
    return send_from_directory("/build", "index.html")


@app.route("/query_pdf/", methods=["POST", "GET"])
def chatPDF():
    if request.method == "POST":
        query = request.form["query"]
        response = find_in_pdf(query)
        return response


def find_in_pdf(query):
    # queryResponse = query_embedding(query, "pdf")
    queryResponse = query_pinecone(query)

    if not queryResponse:
        return jsonify({"message": "Querying to pinecone Error"})

    inputSentence = ""
    ids = ""
    for match in queryResponse["matches"]:
        inputSentence += match["metadata"]["content"]
        ids += match["id"] + " "

    inputSentence = limit_string_tokens(inputSentence, 1000)

    print(ids)
    message = """
            You are a chatbot to assist users with your knowledge. You need to give detailed answer about various user queries.
            You have to use User's language, so for example, if the user asks you something in Dutch, you need to answer in Dutch.
            You are only a language model, so don't pretend to be a human.
            Use the next Context to generate answer about user query. If the Context has no relation to user query, you need to generate answer based on the knowledge that you know.
            And don't mention about the given Context. It is just a reference."""
    try:
        prompt = [
            {"role": "system", "content": f"{message}\nReference:{inputSentence}"},
            {"role": "user", "content": query},
        ]

        return {"type": "generic", "content": generate_text(OPENAI_KEY, prompt)}

    except Exception as e:
        print(traceback.format_exc())
        return "Net Error"


def generate_text(
    openAI_key,
    messages,
    model="gpt-3.5-turbo",
    # model="text-davinci-003",
    # model="text-davinci-002",
):
    speed = 0.05
    summary = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=512,
        n=1,
        stop=None,
        temperature=0.1,
        seed=123,
        # stream=True,
    )
    print(summary.choices[0].message)
    return summary.choices[0].message.content
    # for event in summary:
    #     event_text = event["choices"][0]["text"]
    #     yield event_text


def limit_string_tokens(string, max_tokens=150):
    tokens = string.split()  # Split the string into tokens
    if len(tokens) <= max_tokens:
        return string  # Return the original string if it has fewer or equal tokens than the limit

    # Join the first 'max_tokens' tokens and add an ellipsis at the end
    limited_string = " ".join(tokens[:max_tokens])
    return limited_string


def query_pinecone(query):
    _, embeddings, _ = get_embedding([query], "query")
    if len(embeddings) == 0:
        return jsonify({"message": "Creating Embedding Error"})
    print(embeddings)
    try:
        query_res = PINECONE_INDEX.query(
            top_k=5,
            include_values=True,
            include_metadata=True,
            vector=embeddings[0].tolist(),
        )
        return query_res
        # grouped_sentences = {}
        # for result in query_res['matches']:
        #     vector_id = result['id']
        #     file_name = re.search(r"vec\d+-(.+)\.pdf", vector_id).group(1)
        #     print(file_name)
        #     if file_name not in grouped_sentences:
        #         grouped_sentences[file_name] = []
        #     grouped_sentences[file_name].append(result['metadata']['sentence'])

        # return grouped_sentences

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"message": "Error in Pinecone"})


if __name__ == "__main__":
    app.run(debug=False)
    # serve(app, host="0.0.0.0", port=5000)
