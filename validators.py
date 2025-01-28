from pydantic import BaseModel
import datetime


class registerUserModel(BaseModel):
    first_name:     str
    second_name:    str
    birth_date:     datetime.date
    username:       str
    password:       str
                 
class loginUserModel(BaseModel):
    username: str
    password: str

class authorCreateModel(BaseModel):
    name:       str
    bio:        str
    birth_date: datetime.date


class bookCreateModel(BaseModel):
    name:             str
    description:      str
    publication_date: datetime.date
    author_id:        int
    genre:            str