"""
Vendo Mis Libros Bot

This is a quite simple bot that enlists the books available as options and
returns the information of the book to be sold. Feel free to take this as a
template :)
"""

import logging
import os
import urllib.request
import json
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_API = os.getenv("BOT_API")
BOOKS_URL = "https://melanynadine.github.io/tempbookstore/BooksList.json"

MESSAGES = {
    "start":"Holas! :) esta es la lista de libros que tengo disponibles. Presiona el que te interesa para ofrecerte detalles. Tambien puedes responder con el título del libro que te interesa, si lo tengo te daré los detalles. Todos los precios son negociables :)",
    "states":[],
    "cancel": ""
}

BOOKS_LIST = json.loads(urllib.request.urlopen(BOOKS_URL).read())["books"]

# Enables logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# sets higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and replies with the welcome message."""
    keyboard = [
        [InlineKeyboardButton(f'{BOOKS_LIST[i]["author"]} - {BOOKS_LIST[i]["title"]}', callback_data=i)]
        for i in range(len(BOOKS_LIST))
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        MESSAGES["start"],
        reply_markup=reply_markup
    )
    
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    book_id = query.data
    await query.from_user.send_message(book_info(book_id))
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user

    await update.message.reply_text(
        MESSAGES["cancel"], reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def book_info(index):
    """Returns the info of the book: author, title, price and photo"""
    img_url = "https://melanynadine.github.io/tempbookstore/img/"
    author = BOOKS_LIST[int(index)]["author"]
    title = BOOKS_LIST[int(index)]["title"]
    price = BOOKS_LIST[int(index)]["price"]
    img = img_url + BOOKS_LIST[int(index)]["imgSrc"]
    response = f'{img}\nTítulo: {title}\nAutor: {author}\nPrecio: {price}'
    return response

def main() -> None:
    """Runs the bot."""
    application = Application.builder().token(BOT_API).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("cancel", cancel))

    # Run the bot until the user presses Ctrl-C, which means it starts the server. Run it on terminal
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()