""" JWT Tokens Authentication module                                       \n
    class JWT_encoder provides token encoding functionality               \n
    class JWT_decoder provides access and refresh token generation       \n
    class JWT_validator provides token signature validation functionality \n
    class JWT_decoder provides token decoding functionality               \n
"""


import jwt
from time import time
from fastapi import Response, Request, HTTPException
from fastapi.responses import RedirectResponse
from config import settings
from db.models import User
from db.core import session

secret_key = settings.SECRET_KEY


class JWTencoder:
    """
    Encodes JWT token by method 'encode'\n
    """

    @staticmethod
    def form_JWT_payload(body: dict, living_time_min: int | None = 10):
        """Forms payload for JWT token"""

        payload = {
            "iss": "Library API Authorization",
        }

        living_time_sec = living_time_min * 60
        payload["exp"] = time() + living_time_sec
        payload["iat"] = time()
        payload.update(body)

        return payload

    @staticmethod
    def form_JWT_header(algorithm: str):
        """Forms header for JWT token"""

        return {"alg": f"{algorithm}", "typ": "JWT"}

    @staticmethod
    def encode(
        body: dict, living_time_min: int | None = 10, algorithm: str | None = "HS256"
    ):
        """Encodes JWT token"""
        header = JWTencoder.form_JWT_header(algorithm)
        payload = JWTencoder.form_JWT_payload(body, living_time_min)
        token = jwt.encode(payload, secret_key, algorithm, header)
        return token


class JWTgenerator:
    """JWT tokens generator \n
    Generates token pair \n
    Use generate_tokens to get pair of tokens in format (access token, refresh token)
    """

    @staticmethod
    def generate_access_token(body: dict, token_lifetime_min: int):
        """Generates access token
        Parameters:
        * body - Useful information which will be stored in payload
        * token_lifetime_min - Life time of access token in minutes
        """
        return JWTencoder.encode(body, token_lifetime_min)

    @staticmethod
    def generate_refresh_token(body: dict, token_lifetime_days: int):
        """Generates refresh token
        Parameters:
        * body - Useful information which will be stored in payload
        * token_lifetime_min - Life time of refresh token in days
        """
        token_lifetime_hours = token_lifetime_days * 24
        token_lifetime_mins = token_lifetime_hours * 60
        return JWTencoder.encode(body, token_lifetime_mins)

    @staticmethod
    def generate_tokens(body: dict):
        """Generates pair of tokens"""
        access_token = JWTgenerator.generate_access_token(
            body, settings.ACCS_TOK_LIFETIME_MIN
        )
        refresh_token = JWTgenerator.generate_refresh_token(
            body, settings.REF_TOK_LIFETIME_DAYS
        )
        return (access_token, refresh_token)


class JWTvalidator:
    """Validates token\n
    Use method 'check' to check token signature
    """

    @staticmethod
    def check(token: str) -> bool:
        """Checks token`s signature"""
        try:
            JWTdecoder.decode(token)
        except:
            return False

        return True


class JWTdecoder:
    """Decodes token \n
    Use 'decode' method to decode token
    """

    @staticmethod
    def decode(token):
        """Decodes token"""
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded_token


class TokenHandler:
    """
    Handles with tokens
    Methods:
    * remove_tokens - removes tokens from user`s cookies
    * set_tokens - sets tokens to user`s cookies
    * get_user_bytoken - returns User (model class) if the token is valid
    """

    @staticmethod
    def remove_tokens(response: Response) -> None:
        """removes tokens from user cookies"""
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")

    @staticmethod
    def set_tokens(user: User, response: Response) -> None:
        """sets tokens to user cookies"""
        if user is None:
            return TokenHandler.remove_tokens(response)

        token_body = {"userId": user.id, "is_admin": user.is_admin}

        access_token, refresh_token = JWTgenerator.generate_tokens(token_body)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    @staticmethod
    def get_user_bytoken(token: str) -> User:
        """returns User (model class) if the token is valid"""
        decoded_token = JWTdecoder.decode(token)
        user_id = decoded_token["userId"]
        user = session.query(User).filter(User.id == user_id).first()
        return user


class Validation:
    """User validation class
    Attributes:
    * is_token_valid - true if token is valid, false if not
    * user - User object of token owner
    * is_admin - true if token owner is admin, false if not
    """

    is_token_valid: bool
    user: User
    is_admin: bool

    def get_user(self) -> User:
        """Returns User object of token owner"""
        return self.user

    def __UserValidation(self, request: Request) -> None:
        """Checks token and raises exceptions if its not valid"""
        access_token = request.cookies["access_token"]
        self.is_token_valid = JWTvalidator.check(access_token)
        self.user = TokenHandler.get_user_bytoken(access_token)
        if self.user is None:
            raise jwt.exceptions.ExpiredSignatureError
        self.is_admin = self.user.is_admin

    def __init__(self, request: Request):
        """Validation constructor"""
        try:
            self.__UserValidation(request)
        except:
            pass

    @classmethod
    def validate(
        cls, request: Request, admin_validation: bool = False
    ) -> RedirectResponse | None:
        """Validates token\n
        If token expired or access token not found redirects to refresh endpoint via RedirectResponse\n
        If token not valid raises an exception
        """
        try:
            cls.__UserValidation(cls, request)
            if admin_validation and not cls.user.is_admin:
                raise jwt.exceptions.InvalidAudienceError
        except jwt.exceptions.ExpiredSignatureError:
            return RedirectResponse(
                url=f"/auth/refresh?redirected_from={request.url.path}"
            )
        except jwt.exceptions.InvalidAudienceError:
            raise HTTPException(status_code=403, detail=f"You have not permission")
        except KeyError:
            return RedirectResponse(
                url=f"/auth/refresh?redirected_from={request.url.path}"
            )
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Auth error. {e}")
        else:
            return None
