from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv, set_key
from typing import Optional, List
from urllib.parse import urlencode
from pydantic import BaseModel
import subprocess
import requests
import uvicorn
import atexit
import hmac
import os

def start_nginx():
    subprocess.run(['sudo', 'service', 'nginx', 'start'], check=True)

def stop_nginx():
    subprocess.run(['sudo', 'service', 'nginx', 'stop'], check=True)

# Register the stop_nginx function to be called at exit
atexit.register(stop_nginx)

load_dotenv()  # take environment variables from .env.

class EventData(BaseModel):
    added_by_uid: Optional[str]
    assigned_by_uid: Optional[str]
    checked: Optional[bool]
    child_order: Optional[int]
    collapsed: Optional[bool]
    content: Optional[str]
    description: Optional[str]
    added_at: Optional[str]
    completed_at: Optional[str]
    due: Optional[str]
    id: Optional[str]
    is_deleted: Optional[bool]
    labels: Optional[List[str]]
    parent_id: Optional[str]
    priority: Optional[int]
    project_id: Optional[str]
    responsible_uid: Optional[str]
    section_id: Optional[str]
    sync_id: Optional[str]
    url: Optional[str]
    user_id: Optional[str]

class Initiator(BaseModel):
    email: Optional[str]
    full_name: Optional[str]
    id: Optional[str]
    image_id: Optional[str]
    is_premium: Optional[bool]

class WebhookPayload(BaseModel):
    event_name: str
    user_id: str
    event_data: EventData
    initiator: Initiator
    version: str

class TodoistAuthorization:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.verification_token = os.getenv("VERIFICATION_TOKEN")
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.refresh_token = None  # Add this line

    def get_authorization_url(self):
        params = {
            "client_id": self.client_id,
            "scope": "data:read,data:write,data:delete,project:delete",
            "state": self.verification_token,
        }
        return f"https://todoist.com/oauth/authorize?{urlencode(params)}"

    def refresh_access_token(self):
        if self.refresh_token is None:
            raise Exception("No refresh token available")

        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }

        response = requests.post("https://todoist.com/oauth/access_token", data=data)
        response.raise_for_status()

        token_info = response.json()
        self.refresh_token = token_info.get("refresh_token")

        # Store the refresh token in the .env file
        set_key(".env", "REFRESH_TOKEN", self.refresh_token)

        return token_info.get("access_token")

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request, payload: WebhookPayload):
    # Verify the HMAC signature
    signature = request.headers.get("X-Todoist-Hmac-SHA256")
    if not verify_signature(signature, await request.body()):
        return JSONResponse(status_code=400, content={"message": "Invalid signature"})

    # Handle the webhook event
    print(f"Received {payload.event_name} event")
    print(payload.dict())

    return JSONResponse(status_code=200, content={"message": "Event received"})

def verify_signature(request: Request):
    verification_token = os.getenv("VERIFICATION_TOKEN")
    received_verification_token = request.headers.get("X-Todoist-Hmac-SHA256")
    if not hmac.compare_digest(verification_token, received_verification_token):
        raise HTTPException(status_code=400, detail="Invalid verification token")

@app.get("/tasks")
async def get_tasks(todoist_token: str):
    response = await requests.get("https://api.todoist.com/rest/v1/tasks", {
        "method": "GET",
        "headers": {
            "Authorization": f"Bearer {todoist_token}"
        }
    })
    
    tasks = await response.json()
    return tasks

@app.get("/authorize")
def authorize():
    auth = TodoistAuthorization()
    return {"url": auth.get_authorization_url()}

if __name__ == "__main__":
    todoist_auth = TodoistAuthorization()
    print(f"Authorization URL: {todoist_auth.get_authorization_url()}")

    DOMAIN=os.getenv("DOMAIN")
    PORT=int(os.getenv("PORT"))
    uvicorn.run(app, host=DOMAIN, port=PORT)
