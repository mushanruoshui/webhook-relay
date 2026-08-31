from fastapi import FastAPI, Request
import uvicorn
import hmac, hashlib
from fastapi import HTTPException

app = FastAPI()

SECRET = "stringst"   # 和创建订阅时保持一致

@app.post("/hook")
async def hook(request: Request):
    body = await request.body()
    body_str = body.decode()

    sig_header = request.headers.get("X-Relay-Signature", "")

    timestamp = sig_header.split(",")[0][2:]
    v1 = sig_header.split(",")[1][3:]
    if not timestamp or not v1:
        raise HTTPException(status_code=401, detail="missing signature header")
    signing_payload = f"{timestamp}.{body_str}"
    expected = hmac.new(SECRET.encode(), signing_payload.encode(), hashlib.sha256).hexdigest()


    if hmac.compare_digest(expected, v1):
        print("签名验证通过")
    else:
        print("签名验证失败")
        raise HTTPException(status_code=401)

    print(f"收到body: {body_str}")
    print(f"签名头: {sig_header}")
    return {"ok": True}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)

