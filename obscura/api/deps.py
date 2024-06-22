from fastapi import Header, HTTPException

from obscura.process import PROCESS


def require_api_token(x_api_token: str = Header()):
    if x_api_token != PROCESS.API_TOKEN:
        raise HTTPException(status_code=401)
