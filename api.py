from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, WebSocket
from pydantic import BaseModel
from starlette.responses import FileResponse

import ai

router = APIRouter()


class Query(BaseModel):
    q: str


@router.get("/")
def read_root():
    return FileResponse("gui/index.html")


@router.get("/health")
def health() -> dict:
    """
    Health check endpoint to verify if the server is running.

    Returns:
        dict: A message indicating the server is running.
    """
    return {"message": "Server is running!"}


@router.post("/ask")
async def ask(q: Annotated[str, Form()]):
    print("Received data:", q)

    s = create_response(q)
    return {"message": s}


@router.post("/generate")
async def generate(q: Query):
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


@router.websocket("/ws")
async def generate_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


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
