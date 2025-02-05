""" Initialization of ORM models \n
    Deletes all tables in DB and creates by models.py
"""

from models import Base
from core import engine

def init_db():                                              # DB INITIALIZATION
    """Drops all tables in database and creates new"""
    Base.metadata.drop_all(engine)                          # DELETES ALL TABLES
    Base.metadata.create_all(engine)                        # CREATES TABLES FROM MODELS

if __name__ == "__main__":
    init_db()
