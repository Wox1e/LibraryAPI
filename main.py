from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from db.models import User, Author, Book
from db.core import session
from hashlib import sha256
from sqlalchemy.orm import load_only
from auth import  JWTvalidator, TokenHandler, Validation
from validators import *


app = FastAPI()

@app.route(path="/auth/refresh", methods=["GET", "POST", "DELETE", "PUT"])
def refresh(request:Request, response:Response = Response()):

    """Endpoint for toking refreshing\n
        Checks refresh token \n
    """

    try:
         refresh_token = request.cookies["refresh_token"]
    except KeyError:
        raise HTTPException(status_code=401, detail="Cannot find refresh token. Login or register via /auth/login or /auth/register")
   
    is_valid = JWTvalidator.check(refresh_token)
    if not is_valid: raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = TokenHandler.get_user_bytoken(refresh_token)
    if user is None: raise HTTPException(status_code=401, detail="User not found")

    try:
        redirected_from = dict(request.query_params)["redirected_from"]
        redirect_response = RedirectResponse(url=redirected_from)
        if redirected_from is not None: 
            TokenHandler.set_tokens(user, redirect_response)
            return redirect_response
    except:
        pass
  
    TokenHandler.set_tokens(user, response)
    response.body = {"status":"Ok", "detail":"Your tokens were refreshed"}
    return response

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
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Cannot create your account. Check request. Error message: {e}")
    
    TokenHandler.set_tokens(user, response)    
    return {"status":"Ok", "detail":"Your account was created"}

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
    if user is None: return {"status":"Failed", "message":"User not found"}
    user_hash = user.password

    if user_hash == hash:
        TokenHandler.set_tokens(user, response)
        return {"status": "Ok", f"detail":"You logged in as {user.username}"}
    else:
        raise HTTPException(401, "Wrong username or password. Check your request")

@app.get("/auth/logout")
def logout(response:Response):
    try:
        TokenHandler.remove_tokens(response)
        return {"status":"Ok", "detail":"You logged out"}
    except:
        return {"status": "Error"}
    


@app.post("/author/create")
def create_author(request:Request, author_input:authorCreateModel):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response

    author = Author(author_input.name, author_input.bio, author_input.birth_date)
    try:
        session.add(author)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Cannot create author. Check request. Error message: {e}")
    
    return {"status":"Ok", "detail":"Author created"}

@app.get("/author/{id}")
def get_author(id:int, request:Request):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response

    if id not in range(-2_147_483_647, 2_147_483_647): raise HTTPException(status_code=400, detail=f"Value out of int range")
    author = session.query(Author).filter(Author.id == id).first()
    return author

@app.get("/author")
def get_all_authors(request:Request):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response

    authors = session.query(Author).all()
    return authors

@app.put("/author/{id}")
def update_author(request:Request, author_input:authorCreateModel, id:int):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response
    

    if id not in range(-2_147_483_647, 2_147_483_647): raise HTTPException(status_code=400, detail=f"Value out of int range")
    author = get_author(id, request)

    try:
        author.name = author_input.name
        author.bio = author_input.bio
        author.birth_date = author_input.birth_date
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Cannot update author information. Check your request. Error message: {e}")

    return {"status": "Ok", "detail":"Author info updated"}

@app.delete("/author/{id}")
def delete_author(request:Request, id:int):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response

    if id not in range(-2_147_483_647, 2_147_483_647): raise HTTPException(status_code=400, detail=f"Value out of int range")

    try:
        author = get_author(id, request)
        if author is None: raise HTTPException(status_code=400, detail=f"Author not found")
        session.delete(author)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot delete author. Check your request. Error message: {e}")
    
    return {"status": "Ok", "detail":"Author deleted"}



@app.post("/book/create")
def create_book(request:Request, book_input:bookCreateModel):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response
    
    if book_input.quantity not in range(-2_147_483_647, 2_147_483_647): raise HTTPException(status_code=400, detail=f"Value out of int range")
    author = session.query(Author).filter(Author.id == book_input.author_id).first()
    if author is None: raise HTTPException(status_code=400, detail=f"Author with author_id = {book_input.author_id} doesnt exist.")

    try:
        book = Book(book_input.name, book_input.description, book_input.publication_date, book_input.author_id, book_input.genre, book_input.quantity)
        session.add(book)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Cannot create new book. Check your request. Error: {e}")
    
    return {"status":"Ok", "detail":"Book was created"}

@app.get("/book/{id}")
def get_book(request:Request, id:int):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response

    if id not in range(-2_147_483_647, 2_147_483_647): raise HTTPException(status_code=400, detail=f"Value out if int range")
    book = session.query(Book).filter(Book.id == id).first()
    return book

@app.get("/book")
def get_all_books(request:Request):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response

    book = session.query(Book).all()
    return book

@app.put("/book/{id}")
def update_book(request:Request, book_input:bookCreateModel, id:int):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response
    
    if id not in range(-2_147_483_647, 2_147_483_647): raise HTTPException(status_code=400, detail=f"id value out of int range")
    if book_input.quantity not in range(-2_147_483_647, 2_147_483_647): raise HTTPException(status_code=400, detail=f"Quantity value out of int range")
    author = session.query(Author).filter(Author.id == book_input.author_id).first()
    if author is None: raise HTTPException(status_code=400, detail=f"Author with author_id = {book_input.author_id} doesnt exist.")
    

    book = get_book(request, id)

    try:
        book.name = book_input.name
        book.description = book_input.description
        book.publication_date = book_input.publication_date
        book.author_id = book_input.author_id
        book.genre = book_input.genre
        book.quantity = book_input.quantity
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Cannot update book. Check your request. Error: {e}")

    return {"status": "Ok", "detail":"Book was updated"}

@app.delete("/book/{id}")
def delete_book(request:Request, id:int):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response

    if id not in range(-2_147_483_647, 2_147_483_647): raise HTTPException(status_code=400, detail=f"Id value out of int range")

    try:
        book = get_book(request, id)
        session.delete(book)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot delete book. Check your request. Error: {e}")
    
    return {"status": "Ok", "detail":"Book was deleted"}



@app.get("/reader")
def get_readers(request:Request):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response
    
    readers = session.query(User).\
    filter(User.is_admin == False).\
    options(load_only(User.id, User.username, User.first_name, User.second_name, User.birth_date)).\
    all()
    
    return readers

@app.get("/reader/{id}")
def get_reader(request:Request, id:int):
    validation_response = Validation.validate(request, True)
    if validation_response is not None: return validation_response
    
    if id not in range(-2_147_483_647, 2_147_483_647): raise HTTPException(status_code=400, detail=f"Id value out of range")

    reader = session.query(User).\
    filter(User.is_admin == False).\
    options(load_only(User.id, User.username, User.first_name, User.second_name, User.birth_date)).\
    filter(User.id == id).\
    first()
    
    return reader
    


@app.get("/profile")
def get_profile(request:Request):
    validation = Validation(request)
    validation_response = validation.validate(request)
    if validation_response is not None: return validation_response
    
    user = validation.get_user()
    return {
        "Username": user.username,
        "First name":user.first_name,
        "Second name":user.second_name,
        "Birth date": user.birth_date
    }

@app.put("/profile")
def update_profile(input_user:updateUserModel, request:Request):
    validation = Validation(request)
    validation_response = validation.validate(request)
    if validation_response is not None: return validation_response

    user = validation.get_user()

    try:
        user.first_name = input_user.first_name
        user.second_name = input_user.second_name
        user.birth_date = input_user.birth_date
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Cannot update profile. Check your request")

    return {"status": "Ok", "detail":"Your profile was updated"}