"""
Change where pretrained models from huggingface will be downloaded (cached) to:
export HF_HOME=/whatever/path/you/want
"""
import os
os.environ["TRANSFORMERS_CACHE"] = "/Users/Alex.Jenkins/Repos/transformers" # deprecated in transformers 5.0.0
os.environ['HF_HOME'] = "/Users/Alex.Jenkins/Repos/transformers"

import time
import torch
from langchain.llms.base import LLM
from llama_index import (
    GPTListIndex,
    PromptHelper,
    ServiceContext,
    SimpleDirectoryReader,
    load_index_from_storage,
    StorageContext
)
from transformers import pipeline

os.environ["OPENAI_API_KEY"] = "random" # prevents openai from being used


def timeit():
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            args = [str(arg) for arg in args]

            print(f"[{(end - start):.8f} seconds]: f({args}) -> {result}")
            return result
        return wrapper
    return decorator


class LocalOPT(LLM):
    # model_name = "facebook/opt-iml-max-30b" (this is a 60gb model)
    model_name = "facebook/opt-iml-1.3b"  # ~2.63gb model
    # https://huggingface.co/docs/transformers/main_classes/pipelines
    pipeline = pipeline(
        "text-generation",
        model=model_name,
        # device="cuda:0",
        model_kwargs={"torch_dtype": torch.bfloat16},
    )

    def _call(self, prompt: str, stop=None):
        response = self.pipeline(prompt, max_new_tokens=256)[0]["generated_text"]
        # only return newly generated tokens
        return response[len(prompt) :]

    @property
    def _identifying_params(self):
        return {"name_of_model": self.model_name}

    @property
    def _llm_type(self):
        return "custom"


@timeit()
def create_index(service_context, data_dir:str="datasets/rick_data/txt", persist_dir:str="datasets/rick_data"):
    print("Creating index")
    # Service Context: a container for your llamaindex index and query
    # https://gpt-index.readthedocs.io/en/latest/reference/service_context.html
    try:
        # loads from disc
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
        print(f"Index loaded: {index}")
    except:
        print("No local cache of model found, downloading from huggingface")

        docs = SimpleDirectoryReader(data_dir).load_data()
        index = GPTListIndex.from_documents(docs, service_context=service_context)
        # saves the index to disk
        index.storage_context.persist(persist_dir=persist_dir)
        print(f"Index created: {index}")
    return index


if __name__ == "__main__":
    llm = LocalOPT()
    prompt_helper = PromptHelper(context_window=2048,num_output=256,chunk_overlap_ratio=0.1)
    service_context = ServiceContext.from_defaults(llm=llm, prompt_helper=prompt_helper,chunk_size=1000)
    # Langchain wrapper for openllm, feeding it our custom LLM which is downloaded from huggingface
    index = create_index(service_context)
    # either way we can now query the index
    query_engine = index.as_query_engine(service_context=service_context)
    print('Query Engine created from index. Querying...')
    response = query_engine.query("What is Rick's ship made out of?")
    print(response)
    print(response.source_nodes)
