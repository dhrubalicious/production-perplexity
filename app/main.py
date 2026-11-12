from fastapi import FastAPI

app = FastAPI(
    title="Production Perplexity API",
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "service": "production-perplexity-backend"}
