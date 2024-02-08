import sys
import webbrowser
import threading
from time import sleep
from typing import List
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse

from utilis.data_utils import ResponseModel
from utilis.abstractions import search_folder_of_pdfs_fx, search_pdfs_fx
app = FastAPI()

@app.post("/search_folder_of_pdfs/", response_model=None)
async def api_search_folder_of_pdfs(folder_path: str, search: str, return_csv: bool = False):
    folder_path_obj = Path(folder_path)
    if not folder_path_obj.exists() or not folder_path_obj.is_dir():
        raise HTTPException(status_code=400, detail="Invalid folder path.")

    return await search_folder_of_pdfs_fx(folder_path_obj, search, return_csv)

@app.post("/search_pdfs/", response_model=ResponseModel)
async def api_search_in_multiple_pdfs(files: List[UploadFile] = File(...), search: str = Form(...)):
    return await search_pdfs_fx(files, search)

@app.get("/")
async def main():
    # Check if running in a PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # If the app is running in a bundled context, adjust the base path to _MEIPASS directory
        base_path = Path(sys._MEIPASS)  # type: ignore - only available in PyInstaller bundles
    else:
        # Otherwise, use the directory of the script
        base_path = Path(__file__).parent

    html_file_path = base_path / "frontend.html"

    with open(html_file_path, "r") as file:
        content = file.read()

    return HTMLResponse(content=content)

@app.get("/favicon.ico")
async def favicon():
    raise HTTPException(status_code=204)

def run_production():
    def run_server(server):
        server.run()

    def open_browser(server):
        host, port = None, None
        if not server.started and not hasattr(server, "servers"):
            sleep(1)
        while not host and not port:
            for server in server.servers:
                for socket in server.sockets:
                    if not socket:
                        continue
                    host, port = socket.getsockname()
                    if host and port:
                        break
                if host and port:
                    break

        webbrowser.open(f"http://{host}:{port}")

    config = uvicorn.Config(app, host="127.0.0.1", port=0, reload=False)
    server = uvicorn.Server(config)
    
    server_thread = threading.Thread(target=run_server, args=(server,))
    browser_thread = threading.Thread(target=open_browser, args=(server,))

    server_thread.start()
    sleep(3)
    browser_thread.start()

    server_thread.join()

if __name__ == "__main__":
    run_production()
    # pyinstaller --onefile --add-data "frontend.html:." api.py
    # uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) # development
