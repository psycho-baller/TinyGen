from tinygen import TinyGen
from db import get_all_messages, get_messages_by_github_username_and_repo_id

from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

# from prompts import full_summary_template, tinygen_prompt_template_with_context, tinygen_prompt_template


class GenDiffInput(BaseModel):
    repoUrl: str
    prompt: str


app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "https://tiny-gen.vercel.app",
    "chrome-extension://okiflhgmoemcbijlcfhihgddnomeigle",
    "chrome-extension://jciifdnfancohlpbnechegapliahanid",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    # allow_methods=["*"],  # Allow all methods for testing
    # allow_headers=["*"],  # Allow all headers for testing
    # allow_origins=origins,
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
async def gen_diff(input: GenDiffInput):
    """
    Generate diff for the given repository and prompt
    @permission: logged-in user
    """
    prompt = input.prompt
    repo_url = input.repoUrl

    tinygen = TinyGen()
    response = await tinygen.call(repo_url=repo_url, prompt=prompt)

    # return StreamingResponse(response, media_type="text/event-stream")
    return JSONResponse({"diff": response})


@app.get("/api/v1/diff/all")
async def get_diff():
    """
    Get all messages from the database
    @permission: admin
    """
    return JSONResponse(get_all_messages())


@app.get("/api/v1/diff")
async def get_diff(github_username: str = None, github_repo_id: str = None):
    """
    Get all messages from the database, optionally filtered by github_username and github_repo_id.
    @permission: logged-in user
    """
    # Check if both parameters are provided
    if not github_username or not github_repo_id:
        return JSONResponse(
            {
                "error": "Both 'github_username' and 'github_repo_id' are required parameters."
            },
            status_code=400,
        )

    try:
        # Fetch messages from the database
        messages = get_messages_by_github_username_and_repo_id(
            github_username=github_username, github_repo_id=github_repo_id
        )

        # Check if messages were found
        if not messages:
            return JSONResponse(
                {
                    "error": "No messages found for the provided username and repository ID."
                },
                status_code=404,
            )

        return JSONResponse(messages)

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error fetching messages: {e}")
        return JSONResponse(
            {"error": "An error occurred while fetching messages."},
            status_code=500,
        )
