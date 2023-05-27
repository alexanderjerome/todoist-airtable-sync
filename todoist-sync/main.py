from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from dotenv import load_dotenv, set_key
from typing import Optional, List
from urllib.parse import urlencode
from pydantic import BaseModel
import logging
import requests
import uvicorn
import hashlib
import hmac
import os



load_dotenv()  # take environment variables from .env.
logging.basicConfig(level=logging.DEBUG)

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
        self.refresh_token = os.getenv("REFRESH_TOKEN")  # Load refresh token from .env
        self.domain_name = os.getenv("DOMAIN")
        self.get_authorization_url()
        logging.info('TodoistAuthorization initialized with client_id=%s, redirect_uri=%s', self.client_id, self.redirect_uri)


    def get_authorization_url(self):
        params = {
            "client_id": self.client_id,
            "scope": "data:read,data:read_write,data:delete,project:delete",
            "state": self.verification_token,
            "redirect_uri": f"https://{self.domain_name}/todoist/oauth_success"
        }
        url = f"https://todoist.com/oauth/authorize?{urlencode(params)}"
        logging.info('Generated authorization URL: %s', url)
        return url
            
    def refresh_access_token(self):
        if self.refresh_token is None:
            logging.info('Refreshing access token...')
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
        logging.info('Refresh token updated: %s', self.refresh_token)
        return self.refresh_token
    
    def exchange_code_for_token(self, code):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        logging.info('Exchanging code for token: %s', code)
        response = requests.post("https://todoist.com/oauth/access_token", data=data)
        response.raise_for_status()

        token_info = response.json()
        logging.info('Received access token: %s', token_info.get("access_token"))
        return token_info.get("access_token")


    def is_refresh_token_valid(self):
        logging.info('Checking if refresh token is valid...')
        try:
            self.refresh_access_token()
            return True
        except:
            return False
    
app = FastAPI()

@app.get("/todoist")
def todoist():
    logging.info('Received GET /todoist')
    auth = TodoistAuthorization()
    if auth.is_refresh_token_valid():
        return {"message": "Refresh token is valid"}
    else:
        return RedirectResponse(url=auth.get_authorization_url(), status_code=status.HTTP_303_SEE_OTHER)

@app.get("/todoist/oauth_success")
def oauth_success(code: str):
    logging.info('Received GET /todoist/oauth_success with code=%s', code)
    auth = TodoistAuthorization()
    access_token = auth.exchange_code_for_token(code)
    return {"message": "Connection successful!", "access_token": access_token}

@app.post("/todoist/webhook")
async def webhook(request: Request, payload: WebhookPayload):
    logging.info('Received POST /todoist/webhook with payload=%s', payload.dict())
    # Verify the HMAC signature
    signature = request.headers.get("X-Todoist-Hmac-SHA256")
    if not verify_signature(signature, await request.body()):
        return JSONResponse(status_code=400, content={"message": "Invalid signature"})

    # Handle the webhook event
    print(f"Received {payload.event_name} event")
    print(payload.dict())

    return JSONResponse(status_code=200, content={"message": "Event received"})

def verify_signature(signature: str, payload: bytes):
    verification_token = os.getenv("VERIFICATION_TOKEN")
    computed_signature = hmac.new(
        verification_token.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_signature, signature)


@app.get("/todoist/tasks")
async def get_tasks(todoist_token: str):
    response = await requests.get("https://api.todoist.com/rest/v1/tasks", {
        "method": "GET",
        "headers": {
            "Authorization": f"Bearer {todoist_token}"
        }
    })
    
    tasks = await response.json()
    return tasks

@app.get("/todoist/authorize")
def authorize():
    auth = TodoistAuthorization()
    return {"url": auth.get_authorization_url()}

if __name__ == "__main__":
    todoist_auth = TodoistAuthorization()
    uvicorn.run(app, host="0.0.0.0", port=8000)
