from typing import List, Union
from fastapi import UploadFile
from fastapi.responses import StreamingResponse

from utilis.data_utils import (FileSearchResult,
                         ResponseModel,
                         df_to_bytes_streaming_response,
                         extract_text_from_pdf,
                         open_pdf_from_path_and_extract_text,
                         response_to_pandas,
                         scan_for_pdfs,
                         search_lines)


async def search_folder_of_pdfs_fx(folder_path_obj, search:str, return_csv: bool) -> Union[ResponseModel, StreamingResponse]:
    response_data = []
    pdf_files = await scan_for_pdfs(folder_path_obj)
    
    for file in pdf_files:  # type: ignore
        text = open_pdf_from_path_and_extract_text(file.filepath)
        results = await search_lines(text, search)
        
        response_data.append(FileSearchResult(
            filename = file.filepath.name,
            search_term = search,
            search_results = results,
            filepath = file.filepath
        ))
    
    response = ResponseModel(results=response_data)
    if return_csv:
        response = await df_to_bytes_streaming_response(response_to_pandas(response))

    return response


async def search_pdfs_fx(files: List[UploadFile], search: str) -> ResponseModel:
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
