import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def insert_to_supabase(
    prompt: str, github_username: str, github_repo_id: str, response: str
):
    try:
        supabase.table("messages").insert(
            {
                "user_message": prompt,
                "github_username": github_username,
                "github_repo_id": github_repo_id,
                "ai_response": response,
            }
        ).execute()
        return "success!"
    except:
        return "error"


def get_all_messages():
    response = supabase.table("messages").select("*").execute()
    return json.loads(response.model_dump_json())
