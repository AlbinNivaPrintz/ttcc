from pydantic import BaseModel


Color = tuple[int, int, int]


class EncounteredColor(BaseModel):
    color: Color
    encountered: bool


class Status(BaseModel):
    code: int
    description: str


class GetColorState(BaseModel):
    status: Status
    colours: dict[int, Color]
    isDay: bool
    inCall: bool
    isBusy: bool


class LockResponse(BaseModel):
    status: Status
    maxtime: float
    hash: str
    ttl: float
