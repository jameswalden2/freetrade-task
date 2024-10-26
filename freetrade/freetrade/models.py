from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, EmailStr, IPvAnyAddress
from pydantic_extra_types.mac_address import MacAddress


class FakerData(BaseModel):
    id: int
    uuid: str
    firstname: str
    lastname: str
    username: str
    password: str
    email: EmailStr
    ip: IPvAnyAddress
    macAddress: MacAddress
    website: AnyHttpUrl
    image: AnyHttpUrl
    pipeline_id: str | None
    pipeline_timestamp: str | None


class FakerResponse(BaseModel):
    data: list[FakerData]
