from typing import Annotated

from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import FileResponse

import ai


app = FastAPI()


class Query(BaseModel):
    q: str


origins = [
    "localhost",
    "127.0.0.1",
    "127.0.0.1:*",
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


@app.get("/health")
def health() -> dict:
    """
    Health check endpoint to verify if the server is running.

    Returns:
        dict: A message indicating the server is running.
    """
    return {"message": "Server is running!"}


@app.post("/ask")
def ask(q: Annotated[str, Form()]):
    print("Received data:", q)

    s = create_response(q)
    return {"message": s}


@app.post("/generate")
def generate(q: Query):
    """
    Call the ollama client to generate a response

    Args:
        q (str): The input query string.

    Returns:
        dict: The generated response.

    """

    # Check if the query is empty
    if not q.q:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    s = create_response(q.q)
    return {"message": s}


def create_response(message: str) -> str:
    """
    Create a response dictionary.

    Args:
        message (str): The message to include in the response.

    Returns:
        dict: A dictionary containing the message.
    """

    print("Received query:", message)
    if message is None:
        return HTTPException(status_code=400, detail="Query string is required")

    # options for model:
    # - deepseek-r1:latest
    # - deepseek-r1:1.5b
    # - deepseek-r1:7b
    # - deepseek-r1:8b
    # - deepseek-r1:14b

    text = ai.generate_response(model="deepseek-r1:7b", question=message)
    ai.generate_audio(text)

    return "Generated .wav at server with TTS: " + text
