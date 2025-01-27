from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Date

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

        