import re
import io
import logging
from typing import List, Optional, Union
from pathlib import Path

import fitz
import pandas as pd
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

class SearchResult(BaseModel):
    line_number: int
    line_string: str
    value_extracted: Union[float, int, None]

class FileSearchResult(BaseModel):
    filepath: Optional[Path] = None
    filename: str
    search_term: str
    search_results: Union[List[SearchResult], str]

class ResponseModel(BaseModel):
    results: List[FileSearchResult]

class PDFFile(BaseModel):
    filepath: Path

LOGGER = logging.getLogger(__name__)

def response_to_pandas(response: ResponseModel) -> pd.DataFrame:
    data_rows = []
    # Iterate through each FileSearchResult
    for file_result in response.results:
        # Check if search_results is a string or a list of SearchResult
        if isinstance(file_result.search_results, str):
            # Handle the case where search_results is a string (e.g., error message or no results)
            data_rows.append({
                "filepath": file_result.filepath,
                "filename": file_result.filename,
                "search_term": file_result.search_term,
                "line_number": None,
                "line_string": file_result.search_results,  # You could use this to indicate an error or no results
                "value_extracted": None
            })
        else:
            # Handle the case where search_results is a list of SearchResult instances
            for search_result in file_result.search_results:
                data_rows.append({
                    "filepath": file_result.filepath,
                    "filename": file_result.filename,
                    "search_term": file_result.search_term,
                    "line_number": search_result.line_number,
                    "line_string": search_result.line_string,
                    "value_extracted": search_result.value_extracted
                })
    return pd.DataFrame(data_rows)


async def df_to_bytes_streaming_response(df: pd.DataFrame) -> StreamingResponse:
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    response = StreamingResponse(iter([buffer.getvalue()]), media_type='text/csv')
    # Add a header to the response to prompt download with a filename
    response.headers["Content-Disposition"] = "attachment; filename=dataframe.csv"
    return response

    
async def scan_for_pdfs(folder_path: Path) -> list[PDFFile]:
    if not folder_path.exists() or not folder_path.is_dir():
        raise ValueError("Provided path is not a valid directory")

    pdf_files = []
    LOGGER.info(f"Scanning {folder_path} for PDF files")
    for path in folder_path.rglob('*.pdf'):
        pdf_files.append(PDFFile(filepath=path))
    LOGGER.info(f"Found {len(pdf_files)} PDF files")
    return pdf_files


async def search_lines(text: str, search_string: str):
    results = []
    pattern = re.compile(re.escape(search_string))
    try:
        for index, line in enumerate(text.splitlines()):
            match = pattern.search(line)
            if match:
                extract = re.search(r"(\d[\d,]+[\.]?\d*)", line[match.end():])
                try:
                    extract = float(extract.group().replace(',', ''))  # type: ignore
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


def open_pdf_from_path_and_extract_text(pdf_path: Path) -> str:
    try:
        doc = fitz.open(str(pdf_path))
        text = ""
        for page in doc:  # Iterate through each page
            text += page.get_text()  # type: ignore
        return text
    except Exception as e:
        print(f"Failed to open or read {pdf_path}: {e}")
        return ""


async def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        # Open the PDF file from bytes
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()  # type: ignore
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {e}")
