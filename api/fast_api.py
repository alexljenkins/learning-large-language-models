from fastapi.responses import PlainTextResponse
from fastapi import FastAPI

from implementation.llama_index_chroma_db_class import load_from_disk_pipeline

app = FastAPI()

BRAIN = load_from_disk_pipeline('./datasets/steps_data/steps_knowledge')

@app.get("/ask", response_class=PlainTextResponse)
async def ask(question:str):
    global BRAIN
    answer = BRAIN.ask(question)

    return '"' + str(answer) + '"'

