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
