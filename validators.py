from pydantic import BaseModel, Field
import datetime


class registerUserModel(BaseModel):
    first_name:     str = Field(..., max_length=100, min_length=2)
    second_name:    str = Field(..., max_length=100, min_length=2)
    birth_date:     datetime.date
    username:       str = Field(..., max_length=16, min_length=2)
    password:       str = Field(..., max_length=32, min_length=8)
                 
class loginUserModel(BaseModel):
    username: str = Field(..., max_length=16, min_length=2)  
    password: str = Field(..., max_length=32, min_length=8)


class updateUserModel(BaseModel):
    first_name:     str = Field(..., max_length=100, min_length=2)
    second_name:    str = Field(..., max_length=100, min_length=2)
    birth_date:     datetime.date


class authorCreateModel(BaseModel):
    name:       str = Field(..., max_length=100, min_length=2)
    bio:        str = Field(..., max_length=1000, min_length=2)
    birth_date: datetime.date


class bookCreateModel(BaseModel):
    name:             str = Field(..., max_length=64, min_length=2)
    description:      str = Field(..., max_length=1000, min_length=2)
    publication_date: datetime.date
    author_id:        int = Field(..., gt=0)
    genre:            str = Field(..., max_length=32, min_length=2)
    quantity:         int = Field(..., gt=0)


