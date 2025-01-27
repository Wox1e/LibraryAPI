from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from db.models import User
from db.db import session
from hashlib import sha256
from auth import JWT_generator, TokenChecker, JWT_decoder


#RENAME !! <---
class registerUserModel(BaseModel):
    first_name:     str
    second_name:    str
    birth_date:     str
    username:       str
    password:       str
                 
class loginUserModel(BaseModel):
    username: str
    password: str



def set_tokens(user:User, response:Response) -> None:
    token_body = {
        "userId":user.id,
        "is_admin":user.is_admin
    }

    access_token, refresh_token = JWT_generator.generate_tokens(token_body) 
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)




app = FastAPI()

@app.get("/auth/refresh")
def refresh(request:Request, response:Response):

    """Endpoint for toking refreshing\n
        Checks refresh token \n
    """

    try:
         refresh_token = request.cookies["refresh_token"]
    except KeyError:
        return {"status":"Error"}
   
   
    is_valid = TokenChecker.check(refresh_token)

    
    if is_valid:
        decoded_token = JWT_decoder.decode(refresh_token)
        id = decoded_token["userId"]
        user = session.query(User).filter(User.id == id).first()
        set_tokens(user, response)
        return {"status":"Ok"}
    else:
        request.cookies["refresh_token"] = ""
        return {"status":"Failed"}


@app.post("/auth/register")
def register(input_user:registerUserModel, response:Response):
    """Register Endpoint                                \n
        Required parameters:                            \n
        - first_name : First name                       \n
        - second_name : Second name                     \n
        - birth_date : Birth date in format YYYY-MM-DD  \n
        - username : Username                           \n
        - password : Password                           \n

    """
    first_name = input_user.first_name
    second_name = input_user.second_name
    birth_date = input_user.birth_date
    username = input_user.username
    password = input_user.password
    hash = sha256(password.encode('utf-8')).hexdigest()    
    
    user = User(first_name, second_name, birth_date, username, hash)
    
    try:
        session.add(user)
        session.commit()
    except:
        session.rollback()
        return {"status":"Error"}
    
    set_tokens(user, response)    


    return {"status":"Ok"}

@app.post("/auth/login")
def login(input_user:loginUserModel, response:Response):
    """Login Endpoint                                \n
        Required parameters:                            \n
        - username : Username                           \n
        - password : Password                           \n
    """

    username = input_user.username
    password = input_user.password
    hash = sha256(password.encode('utf-8')).hexdigest()    

    user = session.query(User).filter(User.username == username).first()
    user_hash = user.password

    if user_hash == hash:
        set_tokens(user, response)
        return {"status": "Ok"}
    else:
        return {"Status":"Failed"}


