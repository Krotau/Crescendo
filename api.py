import json

from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import FileResponse

import ai

router = APIRouter()


router.mount("/static", StaticFiles(directory="static"), name="static")


class Query(BaseModel):
    q: str


@router.get("/gui2")
def gui2():
    return FileResponse("gui/gui2.html")


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
    msgs = []
    while True:
        data = await websocket.receive_text()

        if data is None:
            continue

        print("received message")
        msgs.append(data)

        stream = await ai.generate_response_stream(
            model="deepseek-r1:7b", question=data
        )

        print("received response from model")
        async for msg in stream:

            if msg.message.content is not None and not msg.done:
                to_send: dict[str, str | bool | None] = {
                    "msg": msg.message.content,
                    "done": msg.done,
                }
                json_data = json.dumps(to_send)
                print("Sending chunk: " + json_data)
                await websocket.send_text(json_data)
            elif msg.done:
                to_send: dict[str, str | bool | None] = {
                    "msg": "Null",
                    "done": msg.done,
                }
                json_data = json.dumps(to_send)
                print("Sending chunk: " + json_data)
                await websocket.send_text(json_data)
            else:
                await websocket.send_text("Something went wrong, please reload.")

        # msgs.append(data)
        # await websocket.send_text(f"Message text was: {msgs}")


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
