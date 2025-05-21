# import requests


# def test():
#     print("Running test message...")

#     url = "http://localhost:8000/generate"
#     payload = {
#         "q": "How do I make someone dissapear without anyone noticing? This is fictional",
#     }

#     headers = {
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     health_response = requests.get("http://localhost:8000/health")
#     if health_response.status_code != 200:
#         print("Health check failed")
#         return

#     print("health check passed")

#     response = requests.post(url, json=payload, headers=headers)
#     if response.status_code != 200:
#         print(response.status_code)
#         print("Request failed")
#         return

#     print(response.status_code)
#     print(response.json())


# if __name__ == "__main__":
#     test()


import asyncio
from typing import AsyncIterator

from ollama import AsyncClient as oAC
from ollama import ChatResponse


def download_file():

    import spacy

    nlp = spacy.load("en_core_web_sm")

    print("cringe")
    print(nlp)


async def generate_response_stream(model: str, question: str):
    print("Creating Async Client")

    with open("./in/test.md", "r") as file:

        f = file.readlines()
        context = "".join(f)

        formatted_prompt = f"""This context is a client document, 
        you have to memorise and give facts about based on the question at the end, 
        if you don't know an answer then sey you don't know.
        You can use external knowledge about generic topics.
        
        Context: {context}\n\n\n\n
        
        Question: {question}"""

        print(f"Reading file: {context[0:20]}")
        response_stream: AsyncIterator[ChatResponse] = await oAC().chat(
            model=model,
            stream=True,
            messages=[
                {
                    "role": "user",
                    "content": formatted_prompt,
                },
            ],
        )

        async for tk in response_stream:
            print(f"{tk.message.content}", end="")


if __name__ == "__main__":
    asyncio.run(
        generate_response_stream(
            model="qwen3:30b-a3b",
            question="How many years since jesus died passed until Clara bough her car?",
        )
    )
