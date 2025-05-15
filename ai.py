import re


from ollama import chat, ChatResponse
from ollama import ListResponse, list


def print_models():
    models: ListResponse = list()
    print("Available models:")
    
    print("===================================")
    for model in models.models:
        print('Name:', model.model)

        if model.size:
            print('  Size (MB):', f'{(model.size.real / 1024 / 1024):.2f}')

        if model.details:
            print('  Format:', model.details.format)
            print('  Family:', model.details.family)
            print('  Parameter Size:', model.details.parameter_size)
            print('  Quantization Level:', model.details.quantization_level)

        print('\n')
    print("===================================")

print("Generating response... (this may take up to a minute)")

question = "What is the capital of France?"

response: ChatResponse = chat(model="deepseek-r1:7b", messages=[
    {
        "role": "user",
        "content": question,
     },
])

def remove_think_tags(response: ChatResponse) -> str:
    """
    Remove <think> tags from the response content and the reasoning inbetween these tags.

    Args:
        response (ChatResponse): The response object from the chat function.

    Returns:
        str: The response content without <think> tags.

    """
    expr = r"<think>.*?</think>\n?"
    trimmed_response_content = re.sub(expr, "", response.message.content or "", flags=re.DOTALL)
    return trimmed_response_content

r = remove_think_tags(response)
print(r)



from kokoro import KPipeline
import soundfile as sf
import torch


# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇪🇸 'e' => Spanish es
# 🇫🇷 'f' => French fr-fr
# 🇮🇳 'h' => Hindi hi
# 🇮🇹 'i' => Italian it
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇧🇷 'p' => Brazilian Portuguese pt-br
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]
pipeline = KPipeline(lang_code='a') # <= make sure lang_code matches voice, reference above.

text = "Tony is the best. He is a great friend. He is a good person. He is a good friend. He is a good person. He is a good friend. He is a good person. He is a good friend. He is a good person. He is a good friend. He is a good person."

generator = pipeline(
    text, voice='af_heart', # <= change voice here
    speed=1, split_pattern=r'\n+'
)

for i, (gs, ps, audio) in enumerate(generator):
    print(i)  # i => index
    print(gs) # gs => graphemes/text
    print(ps) # ps => phonemes
    sf.write(f'./out/{i}.wav', audio, 24000) # save each audio file