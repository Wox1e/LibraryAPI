from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, CheckConstraint
from hashlib import md5
from db.core import session
from config import settings
from datetime import datetime

Base = declarative_base()

class User(Base):                                                                   # ORM model for user_table
    __tablename__ = "user_table"                                                    # Table name

    id = Column("id", Integer, primary_key=True)                                    # ID            | serial, primary_key
    first_name = Column("first_name", String(100), nullable=False)                  # first_name    | character varying(100), not null
    second_name = Column("second_name", String(100), nullable=False)                # second_name   | character varying(100), not null
    birth_date = Column("birth_date", Date, nullable=False)                         # birth_date    | date, not null
    username = Column("username", String(16), nullable=False, unique=True)          # username      | character varying(16), not null unique
    password = Column("password", String(64), nullable=False)                       # password      | character varying(32), not null
    is_admin = Column("is_admin", Boolean, nullable=False, default=False)           # is_admin      | boolean, not null, default = false


    def __init__(self, 
                 first_name: str, 
                 second_name: str, 
                 birth_date: str, 
                 username:str,
                 password:str,
                 is_admin = False
                 ):
        
        """
        Initialization of new User object.
        
        :param first_name: First_name of the user   \n
        :param second_name: Second_name of the user \n
        :param username: User`s username            \n
        :param password:  Hash of user`s password   \n
        :param birth_date: User`s birth_date        \n
        :param is_admin: If user is admin           \n
        """

        self.first_name = first_name
        self.second_name = second_name
        self.birth_date = birth_date,
        self.username = username
        self.password = password
        self.is_admin = is_admin

class Author(Base):                                                                 # ORM model for author_table
    __tablename__ = "author_table"                                                  # Table name

    id = Column("id", Integer, primary_key=True)                                    # ID            | serial, primary_key                   
    name = Column("name", String(100), nullable=False)                              # name          | character varying(100), not null, unique
    bio = Column("bio", String(1000), nullable=False)                               # bio           | character varying(1000), not null
    birth_date = Column("birth_date", Date, nullable=False)                         # birth_date    | date, not null
    author_hash = Column("author_hash", String(32), nullable=False, unique=True)    # author_hash   | character varying(32), not null, unique

                                                                                    # Author hash uses to store authors with same name and different birth dates
                                                                                    # And not store one author many times

    def __init__(self, 
                 name: str, 
                 bio: str, 
                 birth_date:str,
                 ):
        
        """
        Initialization of new Author object.
        
        :param name: Name of the author                   \n
        :param bio: Author`s biography                    \n
        :param birth_date: Author`s birth date            \n
        """

        self.name = name
        self.bio = bio
        self.birth_date = birth_date,
        self.author_hash = md5(str(name).encode("utf-8") + str(birth_date).encode("utf-8")).hexdigest()

class Book(Base):                                                                   # ORM model for book_table
    __tablename__ = "book_table"                                                    # Table name

    id = Column("id", Integer, primary_key=True)                                                     # ID                   | serial, primary_key
    name = Column("name", String(64), nullable=False)                                                # name                 | character varying(64), not null
    description = Column("description", String(1000), nullable=False)                                # description          | character varying(1000), not null
    publication_date = Column("publication_date", Date, nullable=False)                              # publication_date     | date, not null
    author_id = Column(Integer, ForeignKey("author_table.id"), nullable=False)                       # author_id            | int, foreign key
    genre = Column("genre", String(32), nullable=False)                                              # genre                | character varying(32), not null
    quantity = Column("quantity", Integer, CheckConstraint("quantity >= 0"), nullable=False)         # quantity             | int, not null, check for negative values
    book_hash = Column("book_hash", String(32), nullable=False, unique=True)                         # book_hash            | character varying(32), not null, unique

                                                                                                    # Book hash uses to store books with same name and different publication dates
                                                                                                    # And not allows store one book many times


    def __init__(self, 
                 name: str, 
                 description: str, 
                 publication_date:str,
                 author_id: int, 
                 genre: str,
                 quantity: int
                 ):
        
        """
        Initialization of new Author object.
        
        :param name: Name of the author                   \n
        :param bio: Author`s biography                    \n
        :param birth_date: Author`s birth date            \n
        :param quantity: Book quantity                    \n
        """

        self.name = name
        self.description = description
        self.publication_date = publication_date
        self.author_id = author_id
        self.genre = genre
        self.quantity = quantity
        self.book_hash = md5(str(name).encode("utf-8") + str(publication_date).encode("utf-8")).hexdigest()

class Rent(Base):                                                                   # ORM model for rent_table
    __tablename__ = "rent_table"                                                                    # Table name

    rent_id = Column("rent_id", Integer, primary_key=True)                                          # rent_id    | serial, primary key
    reader_id = Column("reader_id", Integer, ForeignKey("user_table.id"), nullable=False)           # reader_id  | int, foreign key to user_table (id column), not null
    book_id = Column("book_id", ForeignKey("book_table.id"), nullable=False)                        # book_id    | int, foreign key to book_table (id column), not null
    issue_date = Column("issue_date", Date, nullable=False)                                         # issue_date | date, not null
    return_date = Column("return_date", Date, nullable=False)                                       # return_date| date, not null


    class BooksLimitExceed(Exception):
        reason:str = f"User already have {settings.BOOKS_LIMIT_FOR_READER} rented books"

    
    def __checkBooksLimit(self, reader_id:int) -> None:
        """Raises BooksLimitExceed exception if user already rented limit amount books"""
        rented_books = session.query(Rent).filter(Rent.reader_id == reader_id)
        if(rented_books.count() >= settings.BOOKS_LIMIT_FOR_READER): raise self.BooksLimitExceed


    def __init__(self, 
                 reader_id: int, 
                 book_id: int, 
                 return_date: str,
                 ):
        
        """
        Initialization of new Rent object.
        
        :param reader_id: ID of user who rents book                   \n
        :param book_id: ID of rented book                             \n
        :param return_date: Return date                               \n
        """
        self.__checkBooksLimit(reader_id)

        self.reader_id = reader_id
        self.book_id = book_id
        self.issue_date =  datetime.today().strftime('%Y-%m-%d')
        self.return_date = return_date
