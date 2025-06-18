from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, world"}


def start(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI app with Uvicorn."""
    import uvicorn
    uvicorn.run("src.endpoint.main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start()
