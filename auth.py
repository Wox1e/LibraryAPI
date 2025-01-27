import jwt
from config import settings
from time import time

secret_key = settings.SECRET_KEY

class JWT_encoder:
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
        header = JWT_encoder.form_JWT_header(algorightm)
        payload = JWT_encoder.form_JWT_payload(body, living_time_min)
        token = jwt.encode(payload, secret_key, algorightm, header)
        return token

class JWT_generator:

    """JWT tokens generator \n
       Use generate_tokens to get pair of tokens in format (access token, refresh token) 
        
    """

    @staticmethod
    def generate_access_token(body:dict, token_lifetime_min:int):
        return JWT_encoder.encode(body, token_lifetime_min)
    
    @staticmethod
    def generate_refresh_token(body:dict, token_lifetime_days:int):
        token_lifetime_hours = token_lifetime_days * 24
        token_lifetime_mins = token_lifetime_hours * 60
        return JWT_encoder.encode(body, token_lifetime_mins)

    @staticmethod
    def generate_tokens(body:dict):
        access_token = JWT_generator.generate_access_token(body, settings.ACCS_TOK_LIFETIME_MIN)
        refresh_token = JWT_generator.generate_refresh_token(body, settings.REF_TOK_LIFETIME_DAYS)
        return (access_token, refresh_token)


class TokenChecker:
    
    @staticmethod
    def check(token:str) -> bool:

        try:
            JWT_decoder.decode(token)
        except jwt.exceptions.InvalidSignatureError:
            return False
        else:
            return True
        

class JWT_decoder:  
    @staticmethod
    def decode(token):
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded_token