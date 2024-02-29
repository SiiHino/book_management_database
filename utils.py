#importing the necessary libraries and dependencies for the bot to work
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Filter
from aiogram import types
from datetime import datetime, timedelta
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql import text
import asyncio, mapping

#This class is used to create a filter that will be used in the button click handler
class CallbackData(Filter):
    def __init__(self, data):
        self.data = data
    async def check(self, call: types.CallbackQuery) -> bool:
        if call.data == self.data:
            return True
        else: return False

class CallbackStartswith(Filter):
    def __init__(self, data):
        self.data = data
    async def check(self, call: types.CallbackQuery) -> bool:
        if call.data.startswith(self.data):
            return True
        else: return False

#This class is used to determine the states in which the user can be
class user_states(StatesGroup):
    main = State()
    view_books = State()
    keyword_search = State()
    select_genre = State()
    select_book_name = State()
    select_author_name = State()
    select_description = State()
    book_adding = State()
    delete_book = State()
    delete_book_finish = State()

#This class is used for inline bot buttons
class keyboards:

    def __init__(self):
        self.db = database()

    async def main_keyboard(self):

        #this class is used to create a button object
        keyboard = InlineKeyboardMarkup()

        #the following code is used to add buttons to the desired object
        keyboard.add(InlineKeyboardButton("Viewing a list of books", callback_data="view_listbook"))
        keyboard.add(InlineKeyboardButton("Search for a book by keyword", callback_data="keyword_search"))
        keyboard.add(InlineKeyboardButton("Add a new book", callback_data="add_book"))
        keyboard.add(InlineKeyboardButton("Delete a book", callback_data="delete_book"))

        return keyboard

    async def keyword_search(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("<- back to home", callback_data="back"))
        return keyboard
    
    async def genre_select(self):
        keyboard = InlineKeyboardMarkup()
        genres = await self.db.get_all_genres()
        for genre in genres:
            keyboard.add(InlineKeyboardButton(f"{genre.Name}", callback_data=f"genre|{genre.ID}"))
        keyboard.add(InlineKeyboardButton("<- back to home", callback_data="back"))
        return keyboard
    
    async def delete_book(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("<- back to home", callback_data="back"))
        return keyboard


"""
This class is used to interact with the database
"""
class database:

    #func for adding new user in database
    async def add_new_user(self, userID: int, username: str, fullname: str) -> None:
        with sessionmaker(bind=mapping.engine)() as session: #create database session
            user = session.query(mapping.users).filter(mapping.users.ID == userID).first() #check user in database
            if not user:
                """
                if the user is not in the database, we create a new row with the data we need
                """
                user = mapping.users(ID=userID, Username=username, Fullname=fullname)
                session.add(user)
                session.commit()

    async def get_all_books(self):
        with sessionmaker(bind=mapping.engine)() as session:
            return session.query(mapping.books).all()
        
    async def get_books_by_keywords(self, keywords: str):
        with sessionmaker(bind=mapping.engine)() as session:
            data = {
                "Author": session.query(mapping.books).filter(mapping.books.Author.icontains(keywords)).all(),
                "Name": session.query(mapping.books).filter(mapping.books.Name.icontains(keywords)).all(),
                "Description": session.query(mapping.books).filter(mapping.books.Description.icontains(keywords)).all(),
                "Genre": session.query(mapping.books).filter(mapping.books.Genre.icontains(keywords)).all()
            }
            return data
        
    async def delete_book_from_id(self, id: int):
        with sessionmaker(bind=mapping.engine)() as session:
            book = session.query(mapping.books).filter(mapping.books.ID == id).first()
            if not book:
                return False
            else:
                session.delete(book)
                session.commit()
                return True
            
    async def add_new_book_by_genre_name(self, book_name: str, genre_name: str, author: str, description: str):
        with sessionmaker(bind=mapping.engine)() as session:
            book = mapping.books(
                Name = book_name,
                Author = author,
                Description = description,
                Genre = genre_name
            )
            session.add(book)
            genre = session.query(mapping.genres).filter(mapping.genres.Name == genre_name).first()
            if not genre:
                new_genre = mapping.genres(Name = genre_name)
                session.add(new_genre)
            session.commit()

    async def add_new_book_by_genre_id(self, book_name: str, genre_id: int, author: str, description: str):
        with sessionmaker(bind=mapping.engine)() as session:
            genre = session.query(mapping.genres).filter(mapping.genres.ID == genre_id).first()
            book = mapping.books(
                Name = book_name,
                Author = author,
                Description = description,
                Genre = genre.Name
            )
            session.add(book)
            session.commit()

    async def get_all_genres(self):
        with sessionmaker(bind=mapping.engine)() as session:
            return session.query(mapping.genres).all()