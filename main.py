#importing the necessary libraries and dependencies for the bot to work
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os, sys, asyncio
from utils import CallbackStartswith, database, user_states, keyboards, CallbackData

token = "6648401622:AAE-_Dd3YXv3L2FqWrjkzOvfgChIxL7TEVk" #there is a bot token here for our program to work

bot = Bot(token=token, parse_mode="HTML", disable_web_page_preview=True)
"""
This code creates an instance of the bot
with the token specified in the token variable and sets the text parsing mode to "HTML".
It also disables the preview of web pages.
"""

dp = Dispatcher(bot, storage=MemoryStorage())
"""
This code creates an instance of the dispatcher using a bot instanceand in-memory storage.
The dispatcher is used to process incoming messages and perform appropriate actions.
"""

db = database() #This code creates an instance of the class to work with the database
keyboards = keyboards()

#Declaring the processing of the /start command
@dp.message_handler(commands=['start'], state="*")
async def start_command_handler(message: types.Message, state: FSMContext):
	user_fullname = message.from_user.full_name #a variable that stores the user's full_name
	username = message.from_user.username #a variable that stores the user's username
	user_id = message.from_user.id #a variable that stores the user's telegram ID

	#verifying the user and adding it to the database
	await db.add_new_user(user_id, username, user_fullname)

	#The bot's reply message
	bot_message = f"<strong>Hi, {user_fullname}!</strong> I am a bot for managing the library database.\n<i>Choose the action you need:</i>"

	#An instance of an inline button keyboard
	keyboard = await keyboards.main_keyboard()

	#A function for the bot to respond to the user's message
	await message.answer(bot_message, reply_markup=keyboard)

	#a function that allows you to set the user the status of being in the main menu
	await user_states.main.set()

#announcement of a handler for clicking on a button with a list of books
@dp.callback_query_handler(CallbackData("view_listbook"), state=user_states.main)
async def view_listbook_handler(callback: types.CallbackQuery, state: FSMContext):
	books = await db.get_all_books()
	message = "<i><strong>A short list of information about books in the library:</strong></i>"

	message2 = ""
	if len(books) < 1:
		message2 += "<code>There are no books in our library at the moment.</code>"
	else:
		for book in books:
			message2 += f"<strong>Name:</strong> <code>{book.Name}</code>\n<strong>Author:</strong> <code>{book.Author}</code>\n<strong>Genre:</strong> <code>{book.Genre}</code>\n\n"

	message3 = "<strong>For more detailed information about a particular book, use the book title search</strong>\nUse /start for back to main menu"

	#this code edits the message of the bot in which the button was pressed
	await callback.message.edit_text(message)
	await bot.send_message(callback.from_user.id, message2)
	await bot.send_message(callback.from_user.id, message3)

	await user_states.view_books.set()

@dp.callback_query_handler(CallbackData("keyword_search"), state=user_states.main)
async def keyword_search_handler(callback: types.CallbackQuery, state: FSMContext):
	message = "<strong>Send a request to search for books</strong> <i>(This may be the title of the book, part of the description, author or genre)</i>"
	keyboard = await keyboards.keyword_search()
	await callback.message.edit_text(message, reply_markup=keyboard)
	await user_states.keyword_search.set()

@dp.callback_query_handler(CallbackData("back"), state="*")
async def back_to_main_menu_from_keyword_search_handler(callback: types.CallbackQuery, state: FSMContext):
	user_fullname = callback.from_user.full_name 
	bot_message = f"<strong>Hi, {user_fullname}!</strong> I am a bot for managing the library database.\n<i>Choose the action you need:</i>"
	keyboard = await keyboards.main_keyboard()
	await callback.message.edit_text(bot_message, reply_markup=keyboard)
	await user_states.main.set()

@dp.message_handler(state=user_states.keyword_search)
async def keyword_message_handler(message: types.Message, state: FSMContext):
	keywords = message.text
	books = await db.get_books_by_keywords(keywords)

	for search_type in list(books):
		if len(books[search_type]) < 1:
			await message.answer(f"<strong>Books were not found by keyword in the {search_type.upper()} block</strong>")
		else:
			for book in books[search_type]:
				search_message = f"<strong>ID:</strong> <code>{book.ID}</code>\n<strong>Name:</strong> <code>{book.Name}</code>\n<strong>Author:</strong> <code>{book.Author}</code>\n<strong>Genre:</strong> <code>{book.Genre}</code>\n<strong>Description:</strong> <i>{book.Description}</i>\n\n<strong>The key was found in the block {search_type.upper()}</strong>"
				await message.answer(search_message)

	await message.answer("Use /start for back to main menu")

@dp.callback_query_handler(CallbackData("add_book"), state=user_states.main)
async def add_book_handler(callback: types.CallbackQuery, state: FSMContext):
	message = "<i>Choose the genre of the new book from the suggested ones or specify your own:</i>"
	keyboard = await keyboards.genre_select()
	await callback.message.edit_text(message, reply_markup=keyboard)
	await user_states.select_genre.set()

@dp.callback_query_handler(CallbackStartswith("genre|"), state=user_states.select_genre)
async def select_genre_handler(callback: types.CallbackQuery, state: FSMContext):
	await state.update_data(genre_id=callback.data.split('|')[1])
	message = "<i>Enter the name of the new book:</i>"
	await callback.message.edit_text(message)
	await user_states.select_book_name.set()

@dp.message_handler(state=user_states.select_genre)
async def select_genre_message_handler(message: types.Message, state: FSMContext):
	await state.update_data(genre_name=message.text)
	bot_message = "<i>Enter the name of the new book:</i>"
	await message.answer(bot_message)
	await user_states.select_book_name.set()

@dp.message_handler(state=user_states.select_book_name)
async def select_book_name_handler(message: types.Message, state: FSMContext):
	await state.update_data(book_name=message.text)
	bot_message = "<i>Introduce the author of the new book:</i>"
	await message.answer(bot_message)
	await user_states.select_author_name.set()

@dp.message_handler(state=user_states.select_author_name)
async def select_author_handler(message: types.Message, state: FSMContext):
	await state.update_data(author=message.text)
	bot_message = "<i>Enter a brief description of the new book:</i>"
	await message.answer(bot_message)
	await user_states.select_description.set()

@dp.message_handler(state=user_states.select_description)
async def select_description_handler(message: types.Message, state: FSMContext):
	description = message.text
	data = await state.get_data()
	author = data["author"]
	book_name = data["book_name"]
	genre_name = None
	try:
		genre_name = data["genre_name"]
	except:
		genre_id = data["genre_id"]
	
	if genre_name:
		await db.add_new_book_by_genre_name(book_name, genre_name, author, description)
	else:
		await db.add_new_book_by_genre_id(book_name, genre_id, author, description)

	bot_message = "<strong>The new book has been added successfully</strong>\nUse /start for back to main menu"
	await message.answer(bot_message)
	await user_states.book_adding.set()

@dp.callback_query_handler(CallbackData("delete_book"), state=user_states.main)
async def delete_book_handler(callback: types.CallbackQuery, state: FSMContext):
	message = "<strong>Enter the ID of the book you want to delete</strong> <i>(You can find out the ID using the book search)</i><strong>:</strong>"
	keyboard = await keyboards.delete_book()
	await callback.message.edit_text(message, reply_markup=keyboard)
	await user_states.delete_book.set()

@dp.message_handler(state=user_states.delete_book)
async def book_id_to_delete_handler(message: types.Message, state: FSMContext):
	id = int(message.text)
	delete_result = await db.delete_book_from_id(id)
	if delete_result:
		bot_message = "<strong>The book was successfully deleted!\nUse /start for back to main menu</strong>"
		await message.answer(bot_message)
		await user_states.delete_book_finish.set()
	else:
		keyboard = await keyboards.delete_book()
		bot_message = "Idi's mistake! Try again. Enter the ID of the book:"
		await message.answer(bot_message, reply_markup=keyboard)
		await user_states.delete_book.set()

async def main():
	await dp.start_polling(bot)
if __name__ == "__main__":
	asyncio.run(main())
"""
This code starts the main function, which asynchronously starts polling the bot.
If the module name is "main", the asyncio.run function is executed,
which starts the main asynchronous loop.
"""