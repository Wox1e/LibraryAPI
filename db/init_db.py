from models import Base
from core import engine

def init_db():                                              # DB INITIALIZATION
    Base.metadata.drop_all(engine)                          # DELETES ALL TABLES
    Base.metadata.create_all(engine)                        # CREATES TABLES FROM MODELS

if __name__ == "__main__":
    init_db()
    


