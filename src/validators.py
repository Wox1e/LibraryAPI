"""Module containing Pydantic models for request validation"""

import datetime
from pydantic import BaseModel, Field, field_validator


class RegisterUserModel(BaseModel):
    """Model for validating user registration requests"""
    first_name: str = Field(..., max_length=100, min_length=2)
    second_name: str = Field(..., max_length=100, min_length=2)
    birth_date: datetime.date
    username: str = Field(..., max_length=16, min_length=2)
    password: str = Field(..., max_length=32, min_length=8)

    @field_validator("birth_date")
    @classmethod
    def check_user_birth_date(cls, value):
        """Validate that birth date is within acceptable range"""
        min_date = datetime.date(1850, 1, 1)
        max_date = datetime.date.today()
        if not min_date <= value <= max_date:
            raise ValueError(f"Birth_date must be between {min_date} and {max_date}")
        return value


class LoginUserModel(BaseModel):
    """Model for validating user login requests"""
    username: str = Field(..., max_length=16, min_length=2)
    password: str = Field(..., max_length=32, min_length=8)


class UpdateUserModel(BaseModel):
    """Model for validating user profile update requests"""
    first_name: str = Field(..., max_length=100, min_length=2)
    second_name: str = Field(..., max_length=100, min_length=2)
    birth_date: datetime.date

    @field_validator("birth_date")
    @classmethod
    def check_user_birth_date(cls, value):
        """Validate that birth date is within acceptable range"""
        min_date = datetime.date(1850, 1, 1)
        max_date = datetime.date.today()
        if not min_date <= value <= max_date:
            raise ValueError(f"Birth_date must be between {min_date} and {max_date}")
        return value


class AuthorCreateModel(BaseModel):
    """Model for validating author creation requests"""
    name: str = Field(..., max_length=100, min_length=2)
    bio: str = Field(..., max_length=1000, min_length=2)
    birth_date: datetime.date

    @field_validator("birth_date")
    @classmethod
    def check_author_birth_date(cls, value):
        """Validate that birth date is within acceptable range"""
        min_date = datetime.date(1, 1, 1)
        max_date = datetime.date.today()
        if not min_date <= value <= max_date:
            raise ValueError(f"Birth_date must be between {min_date} and {max_date}")
        return value


class BookCreateModel(BaseModel):
    """Model for validating book creation requests"""
    name: str = Field(..., max_length=64, min_length=2)
    description: str = Field(..., max_length=1000, min_length=2)
    publication_date: datetime.date
    author_id: int = Field(..., gt=0)
    genre: str = Field(..., max_length=32, min_length=2)
    quantity: int = Field(..., gt=0)

    @field_validator("publication_date")
    @classmethod
    def check_book_publication_date(cls, value):
        """Validate that publication date is within acceptable range"""
        min_date = datetime.date(1, 1, 1)
        max_date = datetime.date.today()
        if not min_date <= value <= max_date:
            raise ValueError(
                f"publication_date must be between {min_date} and {max_date}"
            )
        return value


class BookRentModel(BaseModel):
    """Model for validating book rental requests"""
    reader_id: int
    book_id: int
    return_date: datetime.date

    @field_validator("return_date")
    @classmethod
    def check_book_return_date(cls, value):
        """Validate that return date is not in the past"""
        min_date = datetime.date.today()
        if not min_date <= value:
            raise ValueError(f"return_date must be between not before {min_date}")
        return value


class RentReturnModel(BaseModel):
    """Model for validating book return requests"""
    rent_id: int
