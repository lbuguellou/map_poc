from pydantic import BaseModel

class Address(BaseModel):
    address: str
    latitude: float
    longitude: float