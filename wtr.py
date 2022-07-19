"""Webex Token Renewer - Python Edition

This script is based on the Go version of wtr.  It is used for retrieving and refreshing
Webex integration tokens.

It borrows heavily from the Webex Token Keeper by Chris Lunsford.
"""
import os
import logging
import uuid
from datetime import datetime, timedelta

import webexteamssdk
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

LOG_LEVEL = logging.INFO

WEBEX_CLIENT_ID = os.environ.get("WEBEX_CLIENT_ID")
WEBEX_CLIENT_SECRET = os.environ.get("WEBEX_CLIENT_SECRET")
WEBEX_REDIRECT_URI = os.environ.get("WEBEX_REDIRECT_URI")
WEBEX_SCOPES = os.environ.get("WEBEX_SCOPES")

WEBEX_REDIRECT_URI = WEBEX_REDIRECT_URI if WEBEX_REDIRECT_URI.endswith("/token") else '/'.join([WEBEX_REDIRECT_URI.strip("/"), "token"])
WEBEX_AUTHORIZATION_URL = f"https://webexapis.com/v1/authorize?client_id={WEBEX_CLIENT_ID}&response_type=code&redirect_uri={WEBEX_REDIRECT_URI}&scope={WEBEX_SCOPES}"
print(WEBEX_REDIRECT_URI)

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(LOG_LEVEL)

app = FastAPI(
    title="wtr^2",
    description="Webex Token Retriever/Renewer",
    version="0.1.0",
)
templates = Jinja2Templates(directory="templates")

webex_api = webexteamssdk.WebexTeamsAPI("<<no token needed for integration>>")

class AccessToken(BaseModel):
    """OAuth generated Access Token; with UTC token expiration timestamps."""
    access_token: str
    expires: datetime
    refresh_token: str
    refresh_token_expires: datetime

    @classmethod
    def from_webex_access_token(cls, token: webexteamssdk.AccessToken):
        """Create a new Access Token from a Webex Teams AccessToken object."""
        now = datetime.utcnow()
        return cls(
            access_token=token.access_token,
            expires=now + timedelta(seconds=token.expires_in),
            refresh_token=token.refresh_token,
            refresh_token_expires=(
                now + timedelta(seconds=token.refresh_token_expires_in)
            ),
        )

# Helper Functions
def request_access_token(code: str) -> AccessToken:
    """Request an access token from Webex.

    Exchange an OAuth code for a refreshable access token.
    """
    logger.info("Requesting an access token")
    webex_access_token = webex_api.access_tokens.get(
        client_id=WEBEX_CLIENT_ID,
        client_secret=WEBEX_CLIENT_SECRET,
        code=code,
        redirect_uri=WEBEX_REDIRECT_URI,
    )

    return AccessToken.from_webex_access_token(webex_access_token)


def refresh_access_token(token: AccessToken) -> AccessToken:
    """Refresh a Webex access token."""
    logger.info("Refreshing an access token")
    logger.debug(
        f"Token expires {token.expires.isoformat()}; "
        f"refresh token expires {token.refresh_token_expires.isoformat()}"
    )
    webex_access_token = webex_api.access_tokens.refresh(
        client_id=WEBEX_CLIENT_ID,
        client_secret=WEBEX_CLIENT_SECRET,
        refresh_token=token.refresh_token,
    )

    new_token = AccessToken.from_webex_access_token(webex_access_token)
    logger.debug(f"Refreshed token expires {new_token.expires.isoformat()}")

    return new_token


# Endpoints
@app.get("/", tags=["Web"])
def start_page(request: Request):
    """The WTR start page."""
    logger.info("Serving start page")
    return templates.TemplateResponse("start.html", {"request": request})

@app.get("/authorize", tags=["Web"])
def authorization_redirect():
    """Redirect authorization requests to the Webex OAuth flow."""
    logger.info("Redirecting to Webex OAuth flow")
    user_key = uuid.uuid4()
    return RedirectResponse(
        f"{WEBEX_AUTHORIZATION_URL}&state={user_key}"
    )

@app.get("/token", tags=["Web"])
def token_page(request: Request, state: str, code: str):
    """Success page at the end of the OAuth flow."""
    logger.info("Serving token page")
    user_key = state

    # Request an access token
    token = request_access_token(code)

    # Store the access token
    # TODO: store the access token somewhere
    # store_access_token(token)

    # Provide the information to the user
    return templates.TemplateResponse(
        "token.html",
        {
            "request": request,
            "token": token.json(indent=2),
        },
    )
