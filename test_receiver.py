from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/hook")
async def hook(request: Request):
    body = await request.body()
    print(f"收到原始body: {body!r}")
    try:
        data = await request.json()
    except Exception:
        data = None
    print(f"收到投递: {data}")
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(app, port=9000)
