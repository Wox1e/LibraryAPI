from fastapi import FastAPI, Request, Response
from db.models import User, Author, Book
from db.core import session
from hashlib import sha256
from auth import  JWTvalidator, TokenHandler, UserValidation, AdminValidation
from validators import *


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
    

@app.post("/test")
def test(request:Request):
    try:
        AdminValidation(request)
    except UserValidation.NotAuthorized as e:
        return {"status":"NotAuthorized", "error":str(e.reason)}



@app.post("/author/create")
def create_author(request:Request, author_input:authorCreateModel):
    try:
        AdminValidation(request)
    except UserValidation.NotAuthorized as e:
        return {"status":"NotAuthorized", "error":str(e.reason)}


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
        AdminValidation(request)
    except UserValidation.NotAuthorized as e:
        return {"status":"NotAuthorized", "error":str(e.reason)}


    author = session.query(Author).filter(Author.id == id).first()
    return author

@app.get("/author")
def get_all_authors(request:Request):
    try:
        AdminValidation(request)
    except UserValidation.NotAuthorized as e:
        return {"status":"NotAuthorized", "error":str(e.reason)}

    authors = session.query(Author).all()
    return authors

@app.put("/author/{id}")
def update_author(request:Request, author_input:authorCreateModel, id:int):
    try:
        AdminValidation(request)
    except UserValidation.NotAuthorized as e:
        return {"status":"NotAuthorized", "error":str(e.reason)}
    
    author = get_author(request, id)

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
        AdminValidation(request)
    except UserValidation.NotAuthorized as e:
        return {"status":"NotAuthorized", "error":str(e.reason)}


    try:
        author = get_author(request, id)
        session.delete(author)
        session.commit()
    except:
        {"status":"Failed"}
    
    return {"status": "Ok"}



@app.post("/book/create")
def create_book(request:Request, book_input:bookCreateModel):
    try:
        AdminValidation(request)
    except UserValidation.NotAuthorized as e:
        return {"status":"NotAuthorized", "error":str(e.reason)}
    
    author = session.query(Author).filter(Author.id == book_input.author_id).first()
    if author is None: return {"status":"Error","message":f"Author with author_id = {book_input.author_id} doesnt exist."}

    try:
        book = Book(book_input.name, book_input.description, book_input.publication_date, book_input.author_id, book_input.genre)
        session.add(book)
        session.commit()
    except:
        session.rollback()
        return {"status":"Error", "message":"Cannot create new book"}
    
    return {"status":"Ok"}

@app.get("/book/{id}")
def get_book(request:Request, id:int):
    try:
        AdminValidation(request)
    except UserValidation.NotAuthorized as e:
        return {"status":"NotAuthorized", "error":str(e.reason)}


    book = session.query(Book).filter(Book.id == id).first()
    return book

@app.get("/book")
def get_all_books(request:Request):
    try:
        AdminValidation(request)
    except UserValidation.NotAuthorized as e:
        return {"status":"NotAuthorized", "error":str(e.reason)}

    book = session.query(Book).all()
    return book

@app.put("/book/{id}")
def update_book(request:Request, book_input:bookCreateModel, id:int):
    try:
        AdminValidation(request)
    except UserValidation.NotAuthorized as e:
        return {"status":"NotAuthorized", "error":str(e.reason)}
    
    author = session.query(Author).filter(Author.id == book_input.author_id).first()
    if author is None: return {"status":"Error","message":f"Author with author_id = {book_input.author_id} doesnt exist."}

    book = get_book(request, id)

    try:
        book.name = book_input.name
        book.description = book_input.description
        book.publication_date = book_input.publication_date
        book.author_id = book_input.author_id
        book.genre = book_input.genre
        session.commit()
    except:
        session.rollback()
        return {"status":"Error"}

    return {"status": "Ok"}

@app.delete("/book/{id}")
def delete_book(request:Request, id:int):
    try:
        AdminValidation(request)
    except UserValidation.NotAuthorized as e:
        return {"status":"NotAuthorized", "error":str(e.reason)}


    try:
        book = get_book(request, id)
        session.delete(book)
        session.commit()
    except:
        {"status":"Failed"}
    
    return {"status": "Ok"}