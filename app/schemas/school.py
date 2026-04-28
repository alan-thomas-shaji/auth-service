from pydantic import BaseModel


class SchoolCreateRequest(BaseModel):
    name: str


class SchoolResponse(BaseModel):
    id: str
    name: str
