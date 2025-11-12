from pydantic import BaseModel

class Address(BaseModel):
    locality: str
    address: str
    latitude: float
    longitude: float
    infos: dict