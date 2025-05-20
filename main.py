from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from api import router


app = FastAPI()

app.include_router(router)

origins = [
    "localhost",
    "127.0.0.1",
    "127.0.0.1:*",
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
