import requests
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CommandHandler

from config import config
from helpers import guarantee_token
from keyboards import main_keyboard

# Start handler


@guarantee_token
def start(update, context):
    """ Register clerk and send text what user can do """
    reply = """Hello! This bot allows you to easily hold a spot in line and be notified when you are up next. Go ahead and search for line to join! 😀"""
    context.bot.send_message(chat_id=update.effective_user.id, text=reply, reply_markup=main_keyboard)


start_handler = CommandHandler('start', start)

# Other handler


@guarantee_token
def other(update, context):
    update.message.reply_text('I see! Please send me a photo of yourself, '
                              'so I know what you look like, or send /skip if you don\'t want to.',
                              reply_markup=ReplyKeyboardRemove())


other_handler = CommandHandler('other', other)


# Test handler
@guarantee_token
def test(update, context):
    update.message.reply_text('Keyboard',
                              reply_markup=ReplyKeyboardRemove())


test_handler = CommandHandler('test', test)


# @guarantee_token
# def create_line_prompt(update, context):
#     context.bot.send_message(chat_id=update.effective_user.id, text="How do you want your new line to be named?")
