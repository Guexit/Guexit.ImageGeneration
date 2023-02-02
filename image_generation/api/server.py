from typing import List
from fastapi import FastAPI

logger = logging.getLogger("Neural Search Server")
logger.setLevel(os.getenv("LOGGER_LEVEL", logging.ERROR))

app = FastAPI()

# health check
@app.get("/")
async def root():
    return {"status": "healthy"}