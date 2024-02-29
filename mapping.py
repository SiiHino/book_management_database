#importing the necessary libraries for the database to work
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Text, Date, Float, Numeric, ARRAY, JSON, VARCHAR, DateTime, LargeBinary
from datetime import datetime, timedelta

"""
This script using for database
"""

engine = create_engine(f'sqlite:///DBases/BotMain.db')
Base = declarative_base()
"""
This code creates an SQLite database engine named BotMain.db in the DBases directory.
He then creates a basic model for a declarative approach to creating tables in the database.
"""
###
"""
This class is used to create a table in the database in which the bot users will be stored
"""
class users(Base):
    __tablename__ = "users"
    ID = Column(Integer, primary_key=True)
    Username = Column(String)
    Fullname = Column(String)

"""
This class is used to create a table in the database in which the books
available in the library will be stored
"""
class books(Base):
    __tablename__ = "books"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String)
    Author = Column(String)
    Description = Column(String)
    Genre = Column(Integer)

"""
This class is used to create a table in the database in which
the genres of books will be stored
"""
class genres(Base):
    __tablename__ = "genres"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String)

###
if __name__ == '__main__':
	Base.metadata.create_all(engine)
"""
This code creates all the tables defined in the base model
in the database using the previously created engine.
This happens only when the module is started as the main program,
which is checked using the __name__ check.
"""