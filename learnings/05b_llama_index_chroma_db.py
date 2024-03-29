"""
TrafilaturaWebReader is a web scrapping agent that can extra web data.
"""
from dotenv import load_dotenv

import chromadb
from llama_index import GPTVectorStoreIndex, download_loader

load_dotenv()

TrafilaturaWebReader = download_loader("TrafilaturaWebReader")

loader = TrafilaturaWebReader()
documents = loader.load_data(urls=['https://google.com'])


def create_embedding_store(name):
    chroma_client = chromadb.Client()
    return chroma_client.create_collection(name)

def query_pages(collection, urls, questions):
    docs = TrafilaturaWebReader().load_data(urls)
    index = GPTVectorStoreIndex.from_documents(docs, chroma_collection=collection)
    query_engine = index.as_query_engine()
    for question in questions:
        print(f"Question: {question} \n")
        print(f"Answer: {query_engine.query(question)}")

if __name__ == "__main__":
    url_list = ["https://supertype.ai", "https://supertype.ai/about-us"]
    questions = [
        "Who are the members of Supertype.ai", 
        "What problems are they trying to solve?",
        "What are the important values at the company?"
    ]

    collection = create_embedding_store("supertype")

    query_pages(
        collection,
        url_list,
        questions
    )
