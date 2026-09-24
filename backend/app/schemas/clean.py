from pydantic import BaseModel


class CleanRequest(BaseModel):
    texto: str