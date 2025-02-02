""" Core database managing module \n
    Use 'session' to interact with DB
"""
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config import settings

user = settings.DB_USER
passw = settings.DB_PASS
host = settings.DB_HOST
port = settings.DB_PORT
db_name = settings.DB_NAME

DB_URL = f"postgresql+psycopg://{user}:{passw}@{host}:{port}/{db_name}"

engine = create_engine(        # CREATES ENGINE
    url=DB_URL,                # DB URL
    echo=False,                # PRINT LOGS IN CONSOLE
    pool_size=10,              # MAX CONNECTIONS
    max_overflow=5             # MAX ADDITIONAL CONNECTIONS
)

session = Session(autocommit=False, autoflush=False, bind=engine)
