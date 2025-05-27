from enum import Enum
from typing import AsyncIterator, Optional
from fastapi import WebSocket
from ollama import ChatResponse, Message

from pydantic import BaseModel

from server.ai import Envoy


CONTEXT_SIZE = 40_000
MODEL_SFW = "qwen3:30b-a3b"
MODEL_NSFW_1 = "goekdenizguelmez/JOSIEFIED-Qwen3:8b"


class MessageResponse(BaseModel):
    done: bool
    msg: str
    context_size: int


class ToolInitResponse(BaseModel):
    tool_name: str
    tool_arguments: dict


class ToolResultResponse(BaseModel):
    done: bool
    result: dict


Payload = MessageResponse | ToolInitResponse | ToolResultResponse


class Kind(str, Enum):
    tool_init = 'tool_init'
    tool_result = 'tool_result'
    message = 'message'


class Response(BaseModel):
    kind: Kind
    payload: Payload


class WebsocketHelper:
    def __init__(self, s: WebSocket, e: Envoy) -> None:
        self.socket: WebSocket = s
        self.envoy: Envoy = e
        self.messages: list[Message] = []
        self.context: Optional[str] = None

    async def send(self, obj: str):
        await self.socket.send_text(obj)

    async def parse_call(self, r: ChatResponse):

        if r.message.content:
            self.update_context(r.message.content)

        ctx_len: int = 0
        if self.context:
            ctx_len = len(self.context)

        message_response = MessageResponse.model_validate(dict(
            done=r.done,
            msg=r.message.content,
            context_size=ctx_len
        ))

        response = Response.model_validate(dict(
            kind=Kind.message,
            payload=message_response
        ))

        await self.send(response.model_dump_json())

    async def send_tool_init_response(self, name, arguments):
        tool_response_init = ToolInitResponse.model_validate({
            'tool_name': name,
            'tool_arguments': arguments
        })

        response = Response.model_validate(dict(
            kind=Kind.tool_init,
            payload=tool_response_init
        )) 

        await self.send(response.model_dump_json())

    async def parse_tool_call(self, tool: Message.ToolCall):
        if function_to_call := self.envoy.functions.get(tool.function.name):
            await self.send_tool_init_response(tool.function.name, tool.function.arguments)

            output = function_to_call(**tool.function.arguments)
            
            print('|-- Calling function:', tool.function.name)
            print('|-- Arguments:', tool.function.arguments)
            print('|-- Function output:', output)
            
            self.messages.append(Message.model_validate({
                'role': 'tool',
                'content': str(output),
                'name': tool.function.name
            }))

            return output

        else:
            print('|-- Error! Function', tool.function.name, 'not found')

    def update_context(self, new_context: str):
        if self.context:
            self.context = self.context + new_context
        else:
            self.context = new_context

    async def get_stream(self, enable_tools: bool):
        return await self.envoy.generate_response_stream(
            model=MODEL_SFW, messages=self.messages, enable_tools=enable_tools
        )

    async def parse_stream(self, stream: AsyncIterator[ChatResponse]):
        async for response in stream:
            if response.message.content:
                self.update_context(response.message.content)

            output = None

            if response.message.tool_calls:
                for tool in response.message.tool_calls:
                    self.messages.append(response.message)
                    
                    output = await self.parse_tool_call(tool)

            if output is not None:
                inner_stream = await self.envoy.generate_response_stream(
                   model=MODEL_SFW, messages=self.messages, enable_tools=False 
                )

                async for inner_response in inner_stream:
                    await self.parse_call(inner_response)

            else:
                await self.parse_call(response)

    async def run(self):
        data = await self.socket.receive_text()
        self.messages.append(Message.model_validate({'role': 'user', 'content': data}))
        stream = await self.get_stream(enable_tools=True)
        await self.parse_stream(stream)

