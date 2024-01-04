# Learning Large Language Models and Their Tools

The goal of this repo was to learn how to use the tools and systems of LLMs that have been
created with the release of ChatGPT.

## Learnings

The `learnings` directory contains simple examples of how to use a given package or tool, usually augmented from the docs.

- [LlamaIndex](https://docs.llamaindex.ai/en/stable/getting_started/starter_example.html) to generate embeddings and search for query context from your vectors.
- [HuggingFace](https://huggingface.co/transformers/quickstart.html) to use pretrained models and a standardised interface.
- [LangChain](https://python.langchain.com/docs/get_started/quickstart) interfaces and integrations to models and tools.
- [Chroma Vector Store](https://docs.trychroma.com/getting-started) for an offline embedding database.
- [Chroma DB in LlamaIndex](https://docs.llamaindex.ai/en/stable/examples/vector_stores/chroma_metadata_filter.html#creating-a-chroma-index) using the LlamaIndex package to handle Chroma DB functionality.

## Implementation

The `implementation` directory expands on any learnings or tools used by adding more complexity, linking systems/tools together or by simply wrapping it up into a more usable format (ie, adding a API endpoint or CLI).

- `llama_index_chroma_db_class` converted learnings from LlamaIndex and Croma DB, improving the basic code into a class to store states while running, wrapping it for an API endpoint which can be used to query the index store, send the embeddings to an AI and return the 'answer' to the given question.
