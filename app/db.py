import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
LocalSession = sessionmaker()

def init_db(app):
    database_url = app.config['DATABASE_URL']
    print("DATABASE_URL used:", database_url)
    print("Absolute file URL", os.path.abspath(database_url.replace("sqlite:///", "")))

    if database_url.startswith("sqlite://"):
        engine = create_engine(database_url, 
                               echo=True)
    else:
        # PostgreSQL database
        engine = create_engine(database_url, 
                               echo=False,
                               pool_size=10,
                               max_overflow=20,
                               pool_pre_ping=True,
                )
        
    LocalSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    