"""Main module with FastAPI endpoints"""

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from db.models import User, Author, Book, Rent
from db.core import session
from hashlib import sha256
from sqlalchemy.orm import load_only
from auth import JWTvalidator, TokenHandler, Validation
from validators import *


app = FastAPI()


@app.route(path="/auth/refresh", methods=["GET", "POST", "DELETE", "PUT"])
def refresh(request: Request):
    """
    Endpoint for token refreshing.

    Checks refresh token and generates new access token if valid.

    Args:
        request (Request): The incoming request object containing refresh token in cookies

    Returns:
        Response: New tokens in cookies and redirect/confirmation response

    Raises:
        HTTPException: If refresh token is missing, invalid or user not found
    """

    try:
        refresh_token = request.cookies["refresh_token"]
    except KeyError:
        raise HTTPException(
            status_code=401,
            detail="Cannot find refresh token. Login or register via /auth/login or /auth/register",
        )

    is_valid = JWTvalidator.check(refresh_token)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = TokenHandler.get_user_bytoken(refresh_token)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    try:
        redirected_from = dict(request.query_params)["redirected_from"]
        redirect_response = RedirectResponse(url=redirected_from)
        if redirected_from is not None:
            TokenHandler.set_tokens(user, redirect_response)
            return redirect_response
    except:
        pass

    response = Response(content="Your tokens were refreshed")
    TokenHandler.set_tokens(user, response)
    return response


@app.post("/auth/register")
def register(input_user: RegisterUserModel, response: Response, request: Request):
    """
    Register new user endpoint.

    Creates new user account with provided details.

    Args:
        input_user (registerUserModel): User registration details
        response (Response): Response object to set auth tokens
        request (Request): The incoming request object

    Returns:
        dict: Status message confirming account creation

    Raises:
        HTTPException: If account creation fails
    """
    password = input_user.password
    hash = sha256(password.encode("utf-8")).hexdigest()
    user = User(
        input_user.first_name,
        input_user.second_name,
        input_user.birth_date,
        input_user.username,
        hash,
    )

    try:
        session.add(user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400, detail="Cannot create your account. Check request."
        )

    TokenHandler.set_tokens(user, response)
    return {"status": "Ok", "detail": "Your account was created"}


@app.post("/auth/login")
def login(input_user: LoginUserModel, response: Response):
    """
    User login endpoint.

    Authenticates user credentials and sets auth tokens.

    Args:
        input_user (loginUserModel): Login credentials
        response (Response): Response object to set auth tokens

    Returns:
        dict: Status message confirming successful login

    Raises:
        HTTPException: If credentials are invalid
    """

    password = input_user.password
    hash = sha256(password.encode("utf-8")).hexdigest()

    user = session.query(User).filter(User.username == input_user.username).first()

    if user is None:
        return {"status": "Failed", "message": "User not found"}

    user_hash = user.password

    if user_hash == hash:
        TokenHandler.set_tokens(user, response)
        return {"status": "Ok", "detail": f"You logged in as {user.username}"}
    else:
        raise HTTPException(
            401, detail="Wrong username or password. Check your request"
        )


@app.get("/auth/logout")
def logout(response: Response):
    """
    User logout endpoint.

    Removes auth tokens from response cookies.

    Args:
        response (Response): Response object to remove tokens from

    Returns:
        dict: Status message confirming logout
    """
    try:
        TokenHandler.remove_tokens(response)
        return {"status": "Ok", "detail": "You logged out"}
    except:
        return {"status": "Error"}


@app.post("/author/create")
def create_author(request: Request, author_input: AuthorCreateModel):
    """
    Create new author endpoint.

    Creates new author with provided details. Requires admin privileges.

    Args:
        request (Request): The incoming request object
        author_input (authorCreateModel): Author details

    Returns:
        dict: Status message confirming author creation

    Raises:
        HTTPException: If creation fails or unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    author = Author(author_input.name, author_input.bio, author_input.birth_date)
    try:
        session.add(author)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400, detail="Cannot create author. Check request."
        )

    return {"status": "Ok", "detail": "Author created"}


@app.get("/author/{id}")
def get_author(id: int, request: Request):
    """
    Get author by ID endpoint.

    Retrieves author details by ID. Requires admin privileges.

    Args:
        id (int): Author ID
        request (Request): The incoming request object

    Returns:
        Author: Author details if found

    Raises:
        HTTPException: If ID invalid or unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    if id not in range(-2_147_483_647, 2_147_483_647):
        raise HTTPException(status_code=400, detail="Value out of int range")

    author = session.query(Author).filter(Author.id == id).first()

    return author


@app.get("/author")
def get_all_authors(request: Request):
    """
    Get all authors endpoint.

    Retrieves list of all authors. Requires admin privileges.

    Args:
        request (Request): The incoming request object

    Returns:
        list[Author]: List of all authors

    Raises:
        HTTPException: If unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    authors = session.query(Author).all()
    return authors


@app.put("/author/{id}")
def update_author(request: Request, author_input: AuthorCreateModel, id: int):
    """
    Update author endpoint.

    Updates existing author details. Requires admin privileges.

    Args:
        request (Request): The incoming request object
        author_input (authorCreateModel): Updated author details
        id (int): Author ID to update

    Returns:
        dict: Status message confirming update

    Raises:
        HTTPException: If update fails or unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    if id not in range(-2_147_483_647, 2_147_483_647):
        raise HTTPException(status_code=400, detail="Value out of int range")
    author = get_author(id, request)

    try:
        author.name = author_input.name
        author.bio = author_input.bio
        author.birth_date = author_input.birth_date
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot update author information. Check your request.",
        )

    return {"status": "Ok", "detail": "Author info updated"}


@app.delete("/author/{id}")
def delete_author(request: Request, id: int):
    """
    Delete author endpoint.

    Deletes author by ID. Requires admin privileges.

    Args:
        request (Request): The incoming request object
        id (int): Author ID to delete

    Returns:
        dict: Status message confirming deletion

    Raises:
        HTTPException: If deletion fails or unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    if id not in range(-2_147_483_647, 2_147_483_647):
        raise HTTPException(status_code=400, detail="Value out of int range")

    try:
        author = get_author(id, request)
        if author is None:
            raise HTTPException(status_code=400, detail="Author not found")
        session.delete(author)
        session.commit()
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Cannot delete author. Check your request."
        )

    return {"status": "Ok", "detail": "Author deleted"}


@app.post("/book/create")
def create_book(request: Request, book_input: BookCreateModel):
    """
    Create new book endpoint.

    Creates new book with provided details. Requires admin privileges.

    Args:
        request (Request): The incoming request object
        book_input (bookCreateModel): Book details

    Returns:
        dict: Status message confirming book creation

    Raises:
        HTTPException: If creation fails or unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    if book_input.quantity not in range(-2_147_483_647, 2_147_483_647):
        raise HTTPException(status_code=400, detail="Value out of int range")
    author = session.query(Author).filter(Author.id == book_input.author_id).first()
    if author is None:
        raise HTTPException(
            status_code=400,
            detail=f"Author with author_id = {book_input.author_id} doesn't exist.",
        )

    try:
        book = Book(
            book_input.name,
            book_input.description,
            book_input.publication_date,
            book_input.author_id,
            book_input.genre,
            book_input.quantity,
        )
        session.add(book)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400, detail="Cannot create new book. Check your request."
        )

    return {"status": "Ok", "detail": "Book was created"}


@app.get("/book/{id}")
def get_book(request: Request, id: int):
    """
    Get book by ID endpoint.

    Retrieves book details by ID. Returns different fields based on user role.

    Args:
        request (Request): The incoming request object
        id (int): Book ID

    Returns:
        Book|dict: Full book details for admin, limited details for regular users

    Raises:
        HTTPException: If ID invalid or unauthorized
    """
    validation = Validation(request)
    validation_response = validation.validate(request)
    if validation_response is not None:
        return validation_response
    if id not in range(-2_147_483_647, 2_147_483_647):
        raise HTTPException(status_code=400, detail="Value out if int range")

    is_admin = validation.is_admin

    if is_admin:
        book = session.query(Book).filter(Book.id == id).first()
        return book

    book = (
        session.query(Book)
        .options(
            load_only(
                Book.name,
                Book.description,
                Book.genre,
                Book.publication_date,
                Book.author_id,
                Book.id,
                Book.description,
            )
        )
        .first()
    )

    author = (
        session.query(Author)
        .filter(Author.id == book.author_id)
        .options(load_only(Author.name))
        .first()
    )

    return {
        "Book name": book.name,
        "Description": book.description,
        "Genre": book.genre,
        "Publication date": book.publication_date,
        "Author": author.name,
        "Book Article": book.id,
    }


@app.get("/book")
def get_all_books(request: Request):
    """
    Get all books endpoint.

    Retrieves list of all books. Requires admin privileges.

    Args:
        request (Request): The incoming request object

    Returns:
        list[Book]: List of all books

    Raises:
        HTTPException: If unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    book = session.query(Book).all()
    return book


@app.put("/book/{id}")
def update_book(request: Request, book_input: BookCreateModel, id: int):
    """
    Update book endpoint.

    Updates existing book details. Requires admin privileges.

    Args:
        request (Request): The incoming request object
        book_input (bookCreateModel): Updated book details
        id (int): Book ID to update

    Returns:
        dict: Status message confirming update

    Raises:
        HTTPException: If update fails or unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    if id not in range(-2_147_483_647, 2_147_483_647):
        raise HTTPException(status_code=400, detail="id value out of int range")
    if book_input.quantity not in range(-2_147_483_647, 2_147_483_647):
        raise HTTPException(status_code=400, detail="Quantity value out of int range")
    author = session.query(Author).filter(Author.id == book_input.author_id).first()
    if author is None:
        raise HTTPException(
            status_code=400,
            detail=f"Author with author_id = {book_input.author_id} doesn't exist.",
        )

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
        raise HTTPException(
            status_code=400, detail="Cannot update book. Check your request."
        )

    return {"status": "Ok", "detail": "Book was updated"}


@app.delete("/book/{id}")
def delete_book(request: Request, id: int):
    """
    Delete book endpoint.

    Deletes book by ID. Requires admin privileges.

    Args:
        request (Request): The incoming request object
        id (int): Book ID to delete

    Returns:
        dict: Status message confirming deletion

    Raises:
        HTTPException: If deletion fails or unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    if id not in range(-2_147_483_647, 2_147_483_647):
        raise HTTPException(status_code=400, detail="Id value out of int range")

    try:
        book = get_book(request, id)
        session.delete(book)
        session.commit()
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Cannot delete book. Check your request."
        )

    return {"status": "Ok", "detail": "Book was deleted"}


@app.post("/book/rent")
def rent_book(request: Request, book_input: BookRentModel):
    """
    Rent book endpoint.

    Creates new book rental. Requires admin privileges.

    Args:
        request (Request): The incoming request object
        book_input (bookRentModel): Rental details

    Returns:
        dict: Status message with rental ID

    Raises:
        HTTPException: If rental fails or unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    try:
        rent = Rent(book_input.reader_id, book_input.book_id, book_input.return_date)
    except Rent.BooksLimitExceed as e:
        raise HTTPException(status_code=400, detail=e.reason)

    try:
        book = session.query(Book).filter(Book.id == book_input.book_id).first()
        session.add(rent)
        book.quantity = book.quantity - 1
        session.commit()
    except:
        session.rollback()
        raise HTTPException(
            status_code=400, detail="Cannot rent a book. Check your request"
        )

    return {"status": "Ok", "detail": "Book was rented", "rent_id": rent.rent_id}


@app.post("/book/return")
def return_book(request: Request, rent_input: RentReturnModel):
    """
    Return book endpoint.

    Processes book return. Requires admin privileges.

    Args:
        request (Request): The incoming request object
        rent_input (rentReturnModule): Return details

    Returns:
        dict: Status message confirming return

    Raises:
        HTTPException: If return fails or unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    try:
        rent = session.query(Rent).filter(Rent.rent_id == rent_input.rent_id).first()
        book = session.query(Book).filter(Book.id == rent.book_id).first()
        session.delete(rent)
        book.quantity = book.quantity + 1
        session.commit()
    except:
        session.rollback()
        raise HTTPException(400, detail="Cannot return book")

    return {"status": "Ok", "detail": "Book was returned"}


@app.get("/reader")
def get_readers(request: Request):
    """
    Get all readers endpoint.

    Retrieves list of all non-admin users. Requires admin privileges.

    Args:
        request (Request): The incoming request object

    Returns:
        list[User]: List of all readers

    Raises:
        HTTPException: If unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    readers = (
        session.query(User)
        .filter(User.is_admin == False)
        .options(
            load_only(
                User.id,
                User.username,
                User.first_name,
                User.second_name,
                User.birth_date,
            )
        )
        .all()
    )

    return readers


@app.get("/reader/{id}")
def get_reader(request: Request, id: int):
    """
    Get reader by ID endpoint.

    Retrieves non-admin user details by ID. Requires admin privileges.

    Args:
        request (Request): The incoming request object
        id (int): Reader ID

    Returns:
        User: Reader details if found

    Raises:
        HTTPException: If ID invalid or unauthorized
    """
    validation_response = Validation.validate(request, True)
    if validation_response is not None:
        return validation_response

    if id not in range(-2_147_483_647, 2_147_483_647):
        raise HTTPException(status_code=400, detail="Id value out of range")

    reader = (
        session.query(User)
        .filter(User.is_admin == False)
        .options(
            load_only(
                User.id,
                User.username,
                User.first_name,
                User.second_name,
                User.birth_date,
            )
        )
        .filter(User.id == id)
        .first()
    )

    return reader


@app.get("/profile")
def get_profile(request: Request):
    """
    Get user profile endpoint.

    Retrieves current user's profile details.

    Args:
        request (Request): The incoming request object

    Returns:
        dict: User profile details

    Raises:
        HTTPException: If unauthorized
    """
    validation = Validation(request)
    validation_response = validation.validate(request, False)
    if validation_response is not None:
        return validation_response

    user = validation.get_user()
    return {
        "Username": user.username,
        "First name": user.first_name,
        "Second name": user.second_name,
        "Birth date": user.birth_date,
    }


@app.put("/profile")
def update_profile(input_user: UpdateUserModel, request: Request):
    """
    Update user profile endpoint.

    Updates current user's profile details.

    Args:
        input_user (updateUserModel): Updated profile details
        request (Request): The incoming request object

    Returns:
        dict: Status message confirming update

    Raises:
        HTTPException: If update fails or unauthorized
    """
    validation = Validation(request)
    validation_response = validation.validate(request)
    if validation_response is not None:
        return validation_response

    user = validation.get_user()

    try:
        user.first_name = input_user.first_name
        user.second_name = input_user.second_name
        user.birth_date = input_user.birth_date
        session.commit()
    except:
        session.rollback()
        raise HTTPException(
            status_code=400, detail="Cannot update profile. Check your request"
        )

    return {"status": "Ok", "detail": "Your profile was updated"}
