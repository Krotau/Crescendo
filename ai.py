import re

from ollama import chat, ChatResponse
from ollama import ListResponse, list

from kokoro import KPipeline
import soundfile as sf


def print_models():
    models: ListResponse = list()
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


def generate_response(model: str, question: str) -> str:
    """
    Generate a response from the model using the provided question.

    Args:
        model (str): The model name to use for generating the response.
        question (str): The question to ask the model.

    Returns:
        ChatResponse: The response object from the chat function.

    """
    print("Generating response... (this may take up to a minute)")

    # TODO: add async support (stream = true)
    #  - make async generator for yielding values from async model

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
    response_content: str = remove_think_tags(response)
    return response_content


def remove_think_tags(response: ChatResponse) -> str:
    """
    Remove <think> tags from the response content and the reasoning inbetween these tags.

    Args:
        response (ChatResponse): The response object from the chat function.

    Returns:
        str: The response content without <think> tags.

    """
    expr = r"<think>.*?</think>\n?"
    trimmed_response_content = re.sub(
        expr, "", response.message.content or "", flags=re.DOTALL
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
