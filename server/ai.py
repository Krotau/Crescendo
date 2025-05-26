import re
from enum import Enum

from typing import Any, AsyncIterator, Callable, List, TypeVar, ParamSpec

from ollama import chat, ChatResponse, AsyncClient
from ollama import ListResponse

from kokoro import KPipeline
from pydantic import BaseModel
import soundfile as sf


T = TypeVar("T")
U = TypeVar("U")
P = ParamSpec("P")

EXPR = r"<think>.*?</think>\n?"


class ToolType(str, Enum):
    function = "function"
    object = "object"


class ToolParameters(BaseModel):
    type: ToolType
    properties: Any
    required: List[str]


class FunctionConfig(BaseModel):
    name: str
    description: str
    parameters: ToolParameters


class ToolConfig(BaseModel):
    type: ToolType
    function: FunctionConfig


class Envoy:
    def __init__(self, client: AsyncClient) -> None:
        self.client = client
        self.tools: list[ToolConfig] = []
        self.functions = dict()

    def register(self, description: str, tool_parameters: ToolParameters):

        def wrapper(tool_func: Callable[P, U]) -> Callable[P, U]:

            tool_descriptor = ToolConfig(
                type=ToolType.function,
                function=FunctionConfig(
                    name=tool_func.__name__,
                    description=description,
                    parameters=tool_parameters,
                ),
            )

            print(tool_descriptor.model_dump_json(indent=2))

            self.tools.append(tool_descriptor)
            self.functions.update({tool_func.__name__: tool_func})
            return tool_func

        return wrapper

    async def print_models(self):
        models: ListResponse = await self.client.list()
        print("Available models:")

        print("===================================")
        for model in models.models:
            print("Name:", model.model)

            if model.size:
                print("  Size (MB):", f"{(model.size.real / 1024 / 1024):.2f}")

            if model.details:
                print("  Format:", model.details.format)
                print("  Family:", model.details.family)
                print("  Parameter Size:", model.details.parameter_size)
                print("  Quantization Level:", model.details.quantization_level)

            print("\n")
        print("===================================")

    async def generate_response_stream(self, model: str, messages, ctx: str, enable_tools: bool):
        print("Creating Async Client")

        # formatted_prompt = f"""The context consists of previous questions from the
        #     user and answers you have given to the user. Please include the context when
        #     generating a new answer. 
            
        #     Context: {ctx}\n\n
            
        #     Question: {question}\n\n

        #     When generating an answer, please do not use any fancy symbols or formatting.
        #     Keep it plain text.
        #     """
        print("generating response")

        tools = None
        if enable_tools:
            print("- - - - Running with Tools enable internally")
            tools = [tool.model_dump() for tool in self.tools]

        response_stream: AsyncIterator[ChatResponse] = await self.client.chat(
            model=model,
            stream=True,
            messages=messages,
            tools=tools,
        )

        print("Done generating")
        return response_stream


def generate_response(model: str, question: str) -> str | None:
    """
    Generate a response from the model using the provided question.

    Args:
        model (str): The model name to use for generating the response.
        question (str): The question to ask the model.

    Returns:
        ChatResponse: The response object from the chat function.

    """
    print("Generating response... (this may take up to a minute)")

    response: ChatResponse = chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    # remove <think> tags
    if response.message.content:
        response_content: str = remove_think_tags(response.message.content)
        return response_content


def remove_think_tags(response: str) -> str:
    """
    Remove <think> tags from the response content and the reasoning inbetween these tags.

    Args:
        response (ChatResponse): The response object from the chat function.

    Returns:
        str: The response content without <think> tags.

    """
    
    trimmed_response_content = re.sub(
        EXPR, "", response or "", flags=re.DOTALL
    )
    return trimmed_response_content


def generate_audio(text: str):
    # 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
    # 🇪🇸 'e' => Spanish es
    # 🇫🇷 'f' => French fr-fr
    # 🇮🇳 'h' => Hindi hi
    # 🇮🇹 'i' => Italian it
    # 🇯🇵 'j' => Japanese: pip install misaki[ja]
    # 🇧🇷 'p' => Brazilian Portuguese pt-br
    # 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]
    pipeline = KPipeline(
        lang_code="a"
    )  # <= make sure lang_code matches voice, reference above.

    generator = pipeline(
        text, voice="af_heart", speed=1, split_pattern=r"\n+"  # <= change voice here
    )

    # TODO: make for loop async --> asnc for
    #  - yield values in for loop

    for i, (gs, ps, audio) in enumerate(generator):
        print(i)  # i => index
        print(gs)  # gs => graphemes/text
        print(ps)  # ps => phonemes

        sf.write(f"./out/{i}.wav", audio, 24000)  # save each audio file
