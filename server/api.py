from fastapi import WebSocket, WebSocketDisconnect
from ollama import AsyncClient, Message
from pydantic import BaseModel
from starlette.responses import FileResponse

import server.ai as ai

from loguru import logger

from fastapi import APIRouter

from server.helpers import WebsocketHelper


router = APIRouter()

envoy = ai.Envoy(AsyncClient())


add_param_descriptor = ai.ToolParameters.model_validate(
    {
        "type": "object",
        "properties": {
            "x": {
                "type": "number",
                "description": "first number",
            },
            "y": {
                "type": "number",
                "description": "second number",
            },
        },
        "required": ["x", "y"],
    }
)


@envoy.register("add two numbers together, no matter their size", add_param_descriptor)
def add(x: int, y: int) -> int:
    return x + y


weather_param_descriptor = ai.ToolParameters.model_validate(
    {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The name of the city",
            },
        },
        "required": ["city"],
    }
)


@envoy.register("Get the current weather for a city", weather_param_descriptor)
def get_current_weather(city: str):
    return f"it is 20 degrees celcius in {city}"


file_param_descriptor = ai.ToolParameters.model_validate(
    {
        "type": "object",
        "properties": {
            "file_name": {
                "type": "string",
                "description": "Name of the file to read",
            },
        },
        "required": ["file_name"],
    }
)

@envoy.register("Get the contents of a requested file", file_param_descriptor)
def get_file_by_name(file_name: str):
    return "File/Text The name of the person is Alica"


class Query(BaseModel):
    q: str


@router.get("/")
def read_root():
    return FileResponse("static/index.html")


@router.get("/health")
def health() -> dict:
    """
    Health check endpoint to verify if the server is running.

    Returns:
        dict: A message indicating the server is running.
    """
    return {"message": "Server is running!"}


@router.websocket("/ws")
async def generate_ws(websocket: WebSocket):
    await websocket.accept()

    logger.info("New WebSocket connection!")

    while True:
        try:

            helper = WebsocketHelper(websocket, envoy)
            data = await helper.socket.receive_text()

            logger.info(f"Received data from WebSocket -> '{data}'")

            helper.messages.append(Message.model_validate({'role': 'user', 'content': data}))
            stream = await helper.get_stream(enable_tools=True)
            await helper.parse_stream(stream)

            logger.info("Sending response back to client")

        except WebSocketDisconnect:
            logger.warning("unhandled websocket disconnect!")
            break
