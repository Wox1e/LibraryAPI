from pydantic import BaseModel, Field, field_validator
import datetime


class registerUserModel(BaseModel):
    first_name:     str = Field(..., max_length=100, min_length=2)
    second_name:    str = Field(..., max_length=100, min_length=2)
    birth_date:     datetime.date
    username:       str = Field(..., max_length=16, min_length=2)
    password:       str = Field(..., max_length=32, min_length=8)
                 
    @field_validator("birth_date")
    @classmethod
    def check_user_birth_date(cls, value):
        min_date = datetime.date(1850, 1, 1)
        max_date = datetime.date.today()
        if not (min_date <= value <= max_date):
            raise ValueError(f"Birth_date must be between {min_date} and {max_date}")
        return value


class loginUserModel(BaseModel):
    username: str = Field(..., max_length=16, min_length=2)  
    password: str = Field(..., max_length=32, min_length=8)


class updateUserModel(BaseModel):
    first_name:     str = Field(..., max_length=100, min_length=2)
    second_name:    str = Field(..., max_length=100, min_length=2)
    birth_date:     datetime.date

    @field_validator("birth_date")
    @classmethod
    def check_user_birth_date(cls, value):
        min_date = datetime.date(1850, 1, 1)
        max_date = datetime.date.today()
        if not (min_date <= value <= max_date):
            raise ValueError(f"Birth_date must be between {min_date} and {max_date}")
        return value


class authorCreateModel(BaseModel):
    name:       str = Field(..., max_length=100, min_length=2)
    bio:        str = Field(..., max_length=1000, min_length=2)
    birth_date: datetime.date

    @field_validator("birth_date")
    @classmethod
    def check_author_birth_date(cls, value):
        min_date = datetime.date(1, 1, 1)
        max_date = datetime.date.today()
        if not (min_date <= value <= max_date):
            raise ValueError(f"Birth_date must be between {min_date} and {max_date}")
        return value


class bookCreateModel(BaseModel):
    name:             str = Field(..., max_length=64, min_length=2)
    description:      str = Field(..., max_length=1000, min_length=2)
    publication_date: datetime.date
    author_id:        int = Field(..., gt=0)
    genre:            str = Field(..., max_length=32, min_length=2)
    quantity:         int = Field(..., gt=0)

    @field_validator("publication_date")
    @classmethod
    def check_book_publication_date(cls, value):
        min_date = datetime.date(1, 1, 1)
        max_date = datetime.date.today()
        if not (min_date <= value <= max_date):
            raise ValueError(f"publication_date must be between {min_date} and {max_date}")
        return value


class bookRentModel(BaseModel):
    reader_id:      int
    book_id:        int
    return_date:    datetime.date

    @field_validator("return_date")
    @classmethod
    def check_book_return_date(cls, value):
        min_date = datetime.date.today()
        if not (min_date <= value):
            raise ValueError(f"return_date must be between not before {min_date}")
        return value

class rentReturnModule(BaseModel):
    rent_id: int