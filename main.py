from typing import Union
from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}



@app.post("/generate")
async def generate(q: Union[str, None] = None):
    """
    Call the ollama client to generate a response

    """

    return {"message": "Generate endpoint"}