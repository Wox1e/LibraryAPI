from pydantic import BaseModel

class registerUserModel(BaseModel):
    first_name:     str
    second_name:    str
    birth_date:     str
    username:       str
    password:       str
                 
class loginUserModel(BaseModel):
    username: str
    password: str

class authorCreateModel(BaseModel):
    name:       str
    bio:        str
    birth_date: str


class bookCreateModel(BaseModel):
    name:             str
    description:      str
    publication_date: str
    author_id:        int
    genre:            str