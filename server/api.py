from fastapi import WebSocket
from ollama import AsyncClient, Message
from pydantic import BaseModel
from starlette.responses import FileResponse

import server.ai as ai


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


class Query(BaseModel):
    q: str


@router.get("/gui2")
def gui2():
    return FileResponse("gui/gui2.html")


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


CONTEXT_SIZE = 40_000
MODEL_SFW = "qwen3:30b-a3b"
MODEL_NSFW_1 = "goekdenizguelmez/JOSIEFIED-Qwen3:8b"
MODEL_NSFW_2 = "huihui_ai/qwen3-abliterated:16b"


@router.websocket("/ws")
async def generate_ws(websocket: WebSocket):
    await websocket.accept()
    # full_context: list[str] = []
    while True:
        helper = WebsocketHelper(websocket, envoy)
        data = await helper.socket.receive_text()
        helper.messages.append(Message.model_validate({'role': 'user', 'content': data}))
        stream = await helper.get_stream(enable_tools=True)
        await helper.parse_stream(stream)
