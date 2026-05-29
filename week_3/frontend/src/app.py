import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
# Imports a library that searches for text files containing configurations (.env) 
# and loads them as system environment options.
from dotenv import load_dotenv

# Search up two levels (..) to target the unified .env configuration file
load_dotenv(dotenv_path="../.env")

app = FastAPI(title="Resume Helper Frontend")

# Mount template directory relative to this script
# Initializes the Jinja2 rendering engine.
# Jinja2 is a tool that reads static HTML files from your disk,
# processes any Python-like syntax inside them
# (like injecting your BACKEND_URL variable), 
# and generates a completed webpage.
templates = Jinja2Templates(directory="src/templates")

# Extract downstream destination path environment key
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

# It tells FastAPI: "When someone visits the home address of my website (like http://localhost:8000/)"
# " trigger the python function right below this line."
@app.get("/", response_class=HTMLResponse) #return viewable page
async def read_item(request: Request):
    # Deliver layout sheet, injecting target API routing endpoints dynamically
    return templates.TemplateResponse(
        request=request,
        name="chat_page.html",
        context={"backend_url": BACKEND_URL}
    )