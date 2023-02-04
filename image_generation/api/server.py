from fastapi import FastAPI
import logging
import os

logger = logging.getLogger("Image Generation Server")
logger.setLevel(os.getenv("LOGGER_LEVEL", logging.ERROR))

app = FastAPI()

# health check
@app.get("/")
async def root():
    return {"status": "healthy"}
