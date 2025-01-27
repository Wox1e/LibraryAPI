from fastapi import FastAPI, Request, Response
from db.models import User
from db.core import session
from hashlib import sha256
from auth import  JWTvalidator, TokenHandler
from validators import loginUserModel, registerUserModel




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
   
   
    is_valid = JWTvalidator.check(refresh_token)

    
    if is_valid:
        user = TokenHandler.get_user_bytoken(refresh_token)
        TokenHandler.set_tokens(user, response)
        return {"status":"Ok"}
    else:
        TokenHandler.remove_tokens(response)
        return {"status":"Failed"}
     
@app.post("/auth/register")
def register(input_user:registerUserModel, response:Response, request:Request):
    """Register Endpoint                                \n
        Required parameters:                            \n
        - first_name : First name                       \n
        - second_name : Second name                     \n
        - birth_date : Birth date in format YYYY-MM-DD  \n
        - username : Username                           \n
        - password : Password                           \n

    """
    password = input_user.password
    hash = sha256(password.encode('utf-8')).hexdigest()    
    user = User(input_user.first_name, input_user.second_name, input_user.birth_date, input_user.username, hash)
    
    try:
        session.add(user)
        session.commit()
    except:
        session.rollback()
        return {"status":"Error"}
    
    TokenHandler.set_tokens(user, response)    
    return {"status":"Ok"}

@app.post("/auth/login")
def login(input_user:loginUserModel, response:Response):
    """Login Endpoint                                \n
        Required parameters:                            \n
        - username : Username                           \n
        - password : Password                           \n
    """

    password = input_user.password
    hash = sha256(password.encode('utf-8')).hexdigest()    

    user = session.query(User).filter(User.username == input_user.username).first()
    user_hash = user.password

    if user_hash == hash:
        TokenHandler.set_tokens(user, response)
        return {"status": "Ok"}
    else:
        return {"Status":"Failed"}

@app.get("/auth/logout")
def logout(response:Response):
    try:
        TokenHandler.remove_tokens(response)
        return {"status":"Ok"}
    except:
        return {"status": "Error"}
    
