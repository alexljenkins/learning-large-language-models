"""
Same as 5b but transformed the code into a reusable class that I then used on 2 different
datasets to test the implementation.
See the api and implementation files for this code to see it in action with a API endpoint.
"""

import pickle
from dotenv import load_dotenv

import chromadb
from llama_index import GPTVectorStoreIndex, download_loader

load_dotenv()

class WebQnA:
    def __init__(self) -> None:
        url_reader = download_loader("TrafilaturaWebReader")
        self.loader = url_reader()
        self.urls = set()


    def add_sources(self, source_urls:list[str]|set[str]):
        self.urls.update(source_urls)


    def load_data(self, source_urls:list[str]|set[str]|None = None) -> list:
        if source_urls:
            self.add_sources(source_urls)
        if not self.urls:
            raise ValueError("No sources to load data from. Use add_sources or pass urls to load_data.")

        # only convert to list (required format) at very end to ensure no duplicates
        return self.loader.load_data(list(self.urls))


    def set_embedding_store(self, name:str = 'default') -> None:
        if not hasattr(self, 'empty_store'):
            self.empty_store = chromadb.Client()
            self.empty_store.create_collection(name)


    def encode_data_to_store(self, source_urls:list[str]|set[str]):
        # use empty store every time
        # re-vectorize everything incase new data has been added
        if not hasattr(self, 'empty_store'):
            self.set_embedding_store()
        index = GPTVectorStoreIndex.from_documents(
                                        self.load_data(source_urls),
                                        chroma_collection = self.empty_store
                                    )
        self.knowledge_engine = index.as_query_engine()


    def save_knowledge_to_disk(self, filepath:str):
        with open(f'{filepath}.pkl', 'wb') as file:
            pickle.dump(self.knowledge_engine, file)


    def load_knowledge_from_disk(self, filepath:str):
        with open(f'{filepath}.pkl', 'rb') as file:
            self.knowledge_engine = pickle.load(file)


    def ask(self, question):
        return self.knowledge_engine.query(question)


# below are 2 different datasets used to test the implementation of the class


def initial_load_or_data_fresh_pipeline(url_list:list[str], knowledge_name:str = 'default', save_path:str = './knowledge_engine'):
    brain = WebQnA()
    brain.add_sources(url_list)
    brain.set_embedding_store(knowledge_name)
    brain.encode_data_to_store(url_list)
    brain.save_knowledge_to_disk(save_path)
    return brain


def load_from_disk_pipeline(filepath:str):
    brain = WebQnA()
    brain.load_knowledge_from_disk(filepath)
    return brain


def steps_data():
    with open('./datasets/steps_data/blog_urls.txt', 'r') as file:
        url_list = file.read().splitlines()
    save_filepath = './datasets/steps_data/steps_knowledge'
    # brain = initial_load_or_data_fresh_pipeline(url_list, 'steps', save_filepath)
    brain = load_from_disk_pipeline(save_filepath)
    questions = [
        "List the Seven Steps by placing them into two categories based on how they are used to enhance writing, explain your reasoning.",
        # "What is the easiest of the seven steps for students to master and teachers to implement?",
        # "What are 5 ways to use the Seven Steps to increase creativity in the classroom?"
    ]
    
    for question in questions:
        print(f'Question: {question}')
        print(f'Answer:\n{brain.ask(question)}')
        print('-'*50)


def supertype_data():
    url_list = ["https://supertype.ai", "https://supertype.ai/about-us"]
    questions = [
        "Who are the members of Supertype.ai", 
        "What problems are they trying to solve?",
        "What are the important values at the company?"
    ]
    save_filepath = './datasets/supertype_knowledge'
    # brain = initial_load_or_data_fresh_pipeline(url_list, 'supertype', save_filepath)
    
    brain = load_from_disk_pipeline(save_filepath)

    for question in questions:
        print(brain.ask(question))

if __name__ == "__main__":
    steps_data()
    # supertype_data()
