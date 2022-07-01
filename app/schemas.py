from datetime import datetime
from typing import Union

from pydantic import BaseModel


class FrameCreate(BaseModel):
    frame_name: str
    registered_at: datetime


class Frame(FrameCreate):
    id: int

    class Config:
        orm_mode = True


class FrameOut(Frame):
    url: str


class UserBase(BaseModel):
    username: str


class UserAuth(UserBase):
    hashed_password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
