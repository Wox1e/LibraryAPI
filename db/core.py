from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))         # PYTHON IMPORT FIX
sys.path.append(parent_dir)                                                         #


from config import settings
db_url = f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}" # DB URL



engine = create_engine(                 # CREATES ENGINE
    url=db_url,                         # DB URL
    echo=True,                          # PRINT LOGS IN CONSOLE
    pool_size=10,                       # MAX CONNECTIONS
    max_overflow=5                      # MAX ADDITIONAL CONNECTIONS
)



# session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session(autocommit=False, autoflush=False, bind=engine)



