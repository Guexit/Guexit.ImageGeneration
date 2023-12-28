from typing import List

from pydantic import BaseModel


class MessageServiceBus(BaseModel):
    url: str
    tags: List[str] = []
