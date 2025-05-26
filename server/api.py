import json

from typing import Annotated

from fastapi import Form, HTTPException, WebSocket
from ollama import AsyncClient, ChatResponse, Message
from pydantic import BaseModel
from starlette.responses import FileResponse

import server.ai as ai


from fastapi import APIRouter


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


@envoy.register("add two numbers", add_param_descriptor)
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


CONTEXT_SIZE = 40_000
MODEL_SFW = "qwen3:30b-a3b"
MODEL_NSFW_1 = "goekdenizguelmez/JOSIEFIED-Qwen3:8b"
MODEL_NSFW_2 = "huihui_ai/qwen3-abliterated:16b"



async def send_to_webclient(response: ChatResponse, full_context, websocket):
    context = "".join(full_context)
    context_len = len(context)

    if response.message.content is None:
        return
    
    parsed_resp = ai.remove_think_tags(response.message.content)

    if response.message.content and not response.done:
        full_context.append(response.message.content)

        to_send: dict[str, str | bool | int | None] = {
            "msg": parsed_resp,
            "done": response.done,
            "context_size": context_len,
        }
        json_data = json.dumps(to_send)
        await websocket.send_text(json_data)
    elif response.done:
        to_send: dict[str, str | bool | int | None] = {
            "msg": parsed_resp,
            "done": response.done,
            "context_size": context_len,
        }
        json_data = json.dumps(to_send)
        await websocket.send_text(json_data)
    else:
        print(response)
        await websocket.send_text("Something went wrong, please reload.")


@router.websocket("/ws")
async def generate_ws(websocket: WebSocket):
    await websocket.accept()
    full_context: list[str] = []
    while True:
        data = await websocket.receive_text()
        if data is None:
            continue

        messages: list[Message] = [Message.model_validate({'role': 'user', 'content': data})]
        
        print("Received message...")
        full_context.append(data)

        context = "".join(full_context)
        # context_len = len(context)
        stream = await envoy.generate_response_stream(
            model=MODEL_SFW, messages=messages, ctx=context
        )


        # TODO: Make flow control beter (less if-statements)

        print("Model thinking...")
        async for response in stream:

            print("Response part:")

            output = None  # Initialize output to avoid unbound error
            final_response = None # Initialize output to avoid unbound error

            if response.message.tool_calls:

                
                # TODO: 2 types of response data to sync with client
                #  - normal responses (msg, done, context_size)
                #  - tool responses (tool being used, external/interal (enum), )


                for tool in response.message.tool_calls:
                    if function_to_call := envoy.functions.get(tool.function.name):
                        print(' - - Calling function:', tool.function.name)
                        print(' - - Arguments:', tool.function.arguments)
                        output = function_to_call(**tool.function.arguments)
                        print(' - - Function output:', output)

                        # Add the function response to messages for the model to use
                        messages.append(response.message)
                        messages.append(Message.model_validate({'role': 'tool', 'content': str(output), 'name': tool.function.name}))
                    else:
                        print(' - - Error! Function', tool.function.name, 'not found')

                    print("\n\n")

                if output is not None:



                    # Get final response from model with function outputs
                    final_stream = await envoy.generate_response_stream(model=MODEL_SFW, messages=messages, ctx=context)
                    async for final_response in final_stream:
                        print('Final response:', final_response.message.content)
                        await send_to_webclient(final_response, full_context, websocket) 
                
            else:
                await send_to_webclient(response, full_context, websocket)


        # msgs.append(data)
        # await websocket.send_text(f"Message text was: {msgs}")


def create_response(message: str) -> str | None:
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
    
    if text:
        ai.generate_audio(text)
        return "Generated .wav at server with TTS: " + text
