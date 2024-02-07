import re
from typing import List, Union
from pathlib import Path

from pydantic import BaseModel
import fitz
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

class SearchResult(BaseModel):
    line_number: int
    line_string: str
    value_extracted: Union[float, int, None]

class FileSearchResult(BaseModel):
    filename: str
    search_term: str
    search_results: Union[List[SearchResult], str]  # Use str for error messages

class ResponseModel(BaseModel):
    results: List[FileSearchResult]


async def search_lines(text: str, search_string: str):
    results = []
    pattern = re.compile(re.escape(search_string))
    try:
        for index, line in enumerate(text.splitlines()):
            match = pattern.search(line)
            if match:
                extract = re.search(r"(\d[\d,]+[\.]?\d*)", line)
                try:
                    extract = float(extract.group().replace(',', ''))
                except Exception:
                    extract = None
                result = SearchResult(
                    line_number = index + 1,
                    line_string = line,
                    value_extracted = extract
                )
                results.append(result)
    except ValueError:
        return 'Error: Failed to search PDF.'
    return results

async def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        # Open the PDF file from bytes
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {e}")


@app.post("/search_pdf/")
async def search_in_pdf_file(file: UploadFile, search_string: str):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
        
    file_content = await file.read()
    text = await extract_text_from_pdf(file_content)
    results = await search_lines(text, search_string)
    
    response_data = {
        'filename': file.filename,
        'search_term': search_string,
        'search_results': results
    }
    return JSONResponse(content=response_data)


@app.post("/search_multiple_pdfs/", response_model=ResponseModel)
async def search_in_multiple_pdfs(files: List[UploadFile] = File(...), search: str = Form(...)):
    response_data = []
    
    for file in files:
        filename = file.filename if file.filename else "Unknown Filename"
        if file.content_type != "application/pdf":
            response_data.append(FileSearchResult(
            filename = filename,
            search_term = search,
            search_results = 'Wrong file type'))
            continue

        file_content = await file.read()
        text = await extract_text_from_pdf(file_content)
        results = await search_lines(text, search)
        
        response_data.append(FileSearchResult(
            filename = filename,
            search_term = search,
            search_results = results
        ))
    return ResponseModel(results=response_data)


@app.get("/")
async def main():
    # load content from frontend.html
    with open(Path(__file__).parent / "frontend.html", "r") as file:
        content = file.read()
    return HTMLResponse(content=content)


if __name__ == '__main__':
    uvicorn.run("pdf_api:app", host="0.0.0.0", port=8000, reload=True)
