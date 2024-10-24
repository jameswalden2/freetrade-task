from pydantic import BaseModel, EmailStr


class FakerData(BaseModel):
    id: int
    uuid: str
    firstname: str
    lastname: str
    username: str
    password: str
    email: EmailStr
    ip: str
    macAddress: str
    website: str
    image: str


class FakerResponse(BaseModel):
    data: list[FakerData]
