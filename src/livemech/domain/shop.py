from uuid import UUID,uuid4
from pydantic import BaseModel, Field


class Shop(BaseModel):
    id:UUID = Field(default_factory=uuid4)
    name:str
    description:str|None=None

    def __str__(self)->str:
        return f"{self.name}  [{self.id}]"