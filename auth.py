""" JWT Tokens Autentication module                                       \n
    class JWT_encoder provides token encoding functionality               \n
    class JWT_decoder provides accsess and refresh token generation       \n
    class JWT_validator provides token signature validation functionality \n
    class JWT_decoder provides token decoding functionality               \n
"""

import jwt
from config import settings
from time import time
from db.models import User
from fastapi import Response, Request, HTTPException
from fastapi.responses import RedirectResponse
from db.core import session

secret_key = settings.SECRET_KEY



class JWTencoder:
    """
    Generates JWT token by method 'encode'\n
    """

    @staticmethod
    def form_JWT_payload(body:dict, living_time_min:int|None = 10):
        """Forms payload for JWT token"""

        payload = {
            "iss":"Library API Authtorization",
        }

        living_time_sec = living_time_min * 60
        payload["exp"] = time() + living_time_sec
        payload["iat"] = time()
        payload.update(body)

        return payload

    @staticmethod
    def form_JWT_header(algorightm:str):
        """Forms header for JWT token"""

        return {
            "alg": f"{algorightm}",
            "typ": "JWT"
        }

    @staticmethod
    def encode(body:dict, living_time_min:int|None = 10, algorightm:str|None = "HS256"):
        header = JWTencoder.form_JWT_header(algorightm)
        payload = JWTencoder.form_JWT_payload(body, living_time_min)
        token = jwt.encode(payload, secret_key, algorightm, header)
        return token

class JWTgenerator:

    """JWT tokens generator \n
       Use generate_tokens to get pair of tokens in format (access token, refresh token) 
        
    """

    @staticmethod
    def generate_access_token(body:dict, token_lifetime_min:int):
        return JWTencoder.encode(body, token_lifetime_min)

    @staticmethod
    def generate_refresh_token(body:dict, token_lifetime_days:int):
        token_lifetime_hours = token_lifetime_days * 24
        token_lifetime_mins = token_lifetime_hours * 60
        return JWTencoder.encode(body, token_lifetime_mins)

    @staticmethod
    def generate_tokens(body:dict):
        access_token = JWTgenerator.generate_access_token(body, settings.ACCS_TOK_LIFETIME_MIN)
        refresh_token = JWTgenerator.generate_refresh_token(body, settings.REF_TOK_LIFETIME_DAYS)
        return (access_token, refresh_token)

class JWTvalidator:

    @staticmethod
    def check(token:str) -> bool:

        try:
            JWTdecoder.decode(token)
        except:
            return False
        else:
            return True

class JWTdecoder:
    @staticmethod
    def decode(token):
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded_token

class TokenHandler:

    @staticmethod
    def remove_tokens(response:Response) -> None:
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")

    @staticmethod
    def set_tokens(user:User, response:Response) -> None:
        if user is None: return TokenHandler.remove_tokens(response)

        token_body = {
            "userId":user.id,
            "is_admin":user.is_admin
        }

        access_token, refresh_token = JWTgenerator.generate_tokens(token_body)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    @staticmethod
    def get_user_bytoken(token:str) -> User:
        decoded_token = JWTdecoder.decode(token)
        id = decoded_token["userId"]
        user = session.query(User).filter(User.id == id).first()
        return user




class Validation:

    is_token_valid: bool
    user:           User
    is_admin:       bool     

    def get_user(self) -> User:
        return self.user




    def __UserValidation(self, request:Request) -> None:
        access_token = request.cookies["access_token"]
        self.is_token_valid = JWTvalidator.check(access_token)
        self.user = TokenHandler.get_user_bytoken(access_token)
        if self.user is None: raise self.NotAuthorized("User not found")
        self.is_admin = self.user.is_admin


    def __init__(self, request:Request):
        try:
            self.__UserValidation(request)
        except:
            pass
    
    @classmethod
    def validate(cls, request:Request, admin_validation:bool = False) -> RedirectResponse|None:
        try:
            cls.__UserValidation(cls, request)
            if admin_validation and not cls.user.is_admin: raise jwt.exceptions.InvalidAudienceError
        except jwt.exceptions.ExpiredSignatureError:
            return RedirectResponse(url = f"/auth/refresh?redirected_from={request.url.path}")
        except jwt.exceptions.InvalidAudienceError:
            raise HTTPException(status_code=403, detail=f"You have not permission")
        except KeyError:
            return RedirectResponse(url = f"/auth/refresh?redirected_from={request.url.path}")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Auth error. {e}")
        else:
            return None