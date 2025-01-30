from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from hashlib import md5

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

    id = Column("id", Integer, primary_key=True)                                    # ID                   | serial, primary_key
    name = Column("name", String(64), nullable=False)                               # name                 | character varying(64), not null
    description = Column("description", String(1000), nullable=False)               # description          | character varying(1000), not null
    publication_date = Column("publication_date", Date, nullable=False)             # publication_date     | date, not null
    author_id = Column(Integer, ForeignKey("author_table.id"), nullable=False)      # author_id            | int, foreign key
    genre = Column("genre", String(32), nullable=False)                             # genre                | character varying(32), not null
    quantity = Column("quantity", Integer, nullable=False)                          # quantity             | int, not null
    book_hash = Column("book_hash", String(32), nullable=False, unique=True)        # book_hash            | character varying(32), not null, unique

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