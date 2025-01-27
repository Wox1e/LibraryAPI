from fastapi import FastAPI, Request, Response
from db.models import User, Author
from db.core import session
from hashlib import sha256
from auth import  JWTvalidator, TokenHandler, UserValidation
from validators import loginUserModel, registerUserModel, authorCreateModel




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
    


@app.post("/author/create")
def create_author(request:Request, author_input:authorCreateModel):
    
    try:
        validation = UserValidation(request)
        if not validation.is_admin: raise UserValidation.NotAuthorized
    except UserValidation.NotAuthorized:
        return {"status":"NotAuthorized"}


    author = Author(author_input.name, author_input.bio, author_input.birth_date)
    try:
        session.add(author)
        session.commit()
    except:
        session.rollback()
        return {"status":"Error"}
    return {"status":"Ok"}

@app.get("/author/{id}")
def get_author(id:int, request:Request):

    try:
        validation = UserValidation(request)
        if not validation.is_admin: raise UserValidation.NotAuthorized
    except UserValidation.NotAuthorized:
        return {"status":"NotAuthorized"}


    author = session.query(Author).filter(Author.id == id).first()
    return author

@app.get("/author")
def get_all_authors(request:Request):

    try:
        validation = UserValidation(request)
        if not validation.is_admin: raise UserValidation.NotAuthorized
    except UserValidation.NotAuthorized:
        return {"status":"NotAuthorized"}

    authors = session.query(Author).all()
    return authors

@app.put("/author/{id}")
def update_author(request:Request, author_input:authorCreateModel, id:int):
    
    try:
        validation = UserValidation(request)
        if not validation.is_admin: raise UserValidation.NotAuthorized
    except UserValidation.NotAuthorized:
        return {"status":"NotAuthorized"}
    
    author = get_author(id)

    try:
        author.name = author_input.name
        author.bio = author_input.bio
        author.birth_date = author_input.birth_date
        session.commit()
    except:
        return {"status":"Error"}

    return {"status": "Ok"}

@app.delete("/author/{id}")
def delete_author(request:Request, id:int):

    try:
        validation = UserValidation(request)
        if not validation.is_admin: raise UserValidation.NotAuthorized
    except UserValidation.NotAuthorized:
        return {"status":"NotAuthorized"}


    try:
        author = get_author(id)
        session.delete(author)
        session.commit()
    except:
        {"status":"Failed"}
    
    return {"status": "Ok"}
