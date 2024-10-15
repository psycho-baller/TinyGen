from api.tinygen import TinyGen
from api.db import get_all_messages

from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

# from prompts import full_summary_template, tinygen_prompt_template_with_context, tinygen_prompt_template


class SummarizeFile(BaseModel):
    repoUrl: str
    prompt: str


app = FastAPI(
    docs_url="/api/llm/docs",
    redoc_url="/api/llm/redoc",
    openapi_url="/api/llm/openapi.json",
)

# CORS configuration
origins = [
    "https://www.youtube.com",
    "http://localhost:3000",
    "https://www.tiny-gen.vercel.app",
    "chrome-extension://okiflhgmoemcbijlcfhihgddnomeigle",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["content-type"],
)


@app.get("/api/healthchecker")
def healthchecker():
    return {
        "status": "success",
        "message": "Integrated FastAPI Framework with Next.js and chrome extension successfully!",
    }


@app.post("/api/v1/diff")
async def gen_diff(input: SummarizeFile):
    prompt = input.prompt
    repo_url = input.repoUrl

    tinygen = TinyGen()
    response = tinygen.stream(repo_url=repo_url, prompt=prompt)

    return StreamingResponse(response, media_type="text/event-stream")


@app.get("/api/v1/diff")
async def get_diff():
    return JSONResponse(get_all_messages())
