import os,hmac
from fastapi import Header,HTTPException
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY 环境变量未设置，服务拒绝启动")

def verify_api_key(x_api_key: str = Header(...)):
    if not hmac.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401,detail="Invalid API key")
