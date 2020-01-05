import logging

import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from config import config
from helpers import guarantee_token
from keyboards import main_keyboard

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

SEARCH_LINE = range(1)


def join_line_prompt(update, context):
    update.message.reply_text("Type in the name of a line you want to join:\n"
                              "If you changed your mind type /cancel", reply_markup=ReplyKeyboardRemove())
    return SEARCH_LINE


@guarantee_token
def validate_name(update, context):
    line_name = update.message.text
    url = config['api_url'] + '/clients/get-in-line'
    headers = {"Authorization": "Bearer " + context.user_data.get('token')}
    payload = {"line_name": line_name}
    res = requests.post(url, headers=headers, json=payload)

    logger.info("Got response inside validate_name:\nstatus: {}  type: {}\npayload: {}".format(res.status_code, type(res.status_code), res.json()))

    if res.status_code == 400:
        update.message.reply_text("Line with the name '{}' wasn't found. Check your spelling and try again: ".format(line_name))
        return SEARCH_LINE

    if res.status_code == 200:
        update.message.reply_text(
            "You successfully joined line '{}' ✅. Now you can see list of lines you hold spot in by pressing 'My lines 📋'.".format(line_name),
            reply_markup=main_keyboard)
        return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text('Line creation cancelled.',
                              reply_markup=main_keyboard)

    return ConversationHandler.END


join_line_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(r'Join line ➕'), join_line_prompt)],

    states={
        SEARCH_LINE: [MessageHandler(Filters.text, validate_name)],
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
