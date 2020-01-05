import logging

import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from config import config
from helpers import guarantee_token
from keyboards import main_keyboard

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

CHOOSE_LINE, CHOOSE_ACTION, CALL_NEXT = range(3)


# Helpers
def get_all_lines_names(context):
    """ Returns list of all line names that belong to clerk """
    url = config['api_url'] + '/clients/my-lines'
    headers = {"Authorization": "Bearer " + context.user_data.get('token')}
    res = requests.get(url, headers=headers)
    logger.debug(f'{res.status_code=}')
    logger.debug(f'{res.content=}')
    lines_full = res.json()
    logger.info(f"{lines_full=}")
    lines_names = [x['name'] for x in lines_full]

    return lines_names


def get_line_info(line_name):
    line_info = dict()

    # How many people in line
    url = config['api_url'] + '/lines/get-by-name'
    params = {'line_name': line_name}
    res = requests.get(url, params=params)
    payload = res.json()
    line_info['people_in_line'] = payload.get('people_in_line')

    # Name of current client
    url = config['api_url'] + '/lines/get-current-client'
    params = {'line_name': line_name}
    res = requests.get(url, params=params)
    payload = res.json()
    line_info['current_client'] = payload.get('username', 'Noone')

    # Name of next client
    url = config['api_url'] + '/lines/get-next-client'
    params = {'line_name': line_name}
    res = requests.get(url, params=params)
    payload = res.json()
    line_info['next_client'] = payload.get('username', 'Noone')

    print("Got line_info: {}".format(line_info))

    return line_info

# Keyboards


def lines_list_keyboard(context):
    lines_names = get_all_lines_names(context)

    buttons = [[KeyboardButton(x)] for x in lines_names] + [[KeyboardButton("❌")]]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    return keyboard


def line_management_keyboard():
    buttons = [[KeyboardButton("Call next")], [KeyboardButton("Refresh line info")], [KeyboardButton("🔙")]]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    return keyboard

# Handler functions


@guarantee_token
def display_lines(update, context):
    if not get_all_lines_names(context):
        update.message.reply_text("You don't hold a spot in any line yet. But you can join one:", reply_markup=main_keyboard)
        return ConversationHandler.END

    keyboard = lines_list_keyboard(context)
    update.message.reply_text("Here are your lines:", reply_markup=keyboard)
    return CHOOSE_LINE


@guarantee_token
def choose_line(update, context):
    line_name = update.message.text

    # If imputed line_name is invalid
    if line_name not in get_all_lines_names(context):
        keyboard = lines_list_keyboard(context)
        update.message.reply_text("You haven't created a line named '{}'. Try again:".format(line_name), reply_markup=keyboard)
        return CHOOSE_LINE

    context.user_data['line_name'] = line_name
    line_info = get_line_info(line_name)

    keyboard = line_management_keyboard()

    update.message.reply_text("You are now managing line '{}'.\n"
                              "Current client: {}.\n"
                              "People in line: {}.\n"
                              "Next client: {}.".format(
                                  line_name,
                                  line_info.get('current_client'),
                                  line_info.get('people_in_line'),
                                  line_info.get('next_client')
                              ),
                              reply_markup=keyboard)
    return CHOOSE_ACTION


@guarantee_token
def refresh_line_info(update, context):
    line_name = context.user_data['line_name']

    line_info = get_line_info(line_name)

    keyboard = line_management_keyboard()

    update.message.reply_text("You are now managing line '{}'.\n"
                              "Current client: {}.\n"
                              "People in line: {}.\n"
                              "Next client: {}.".format(
                                  line_name,
                                  line_info.get('current_client'),
                                  line_info.get('people_in_line'),
                                  line_info.get('next_client')
                              ),
                              reply_markup=keyboard)
    return CHOOSE_ACTION


@guarantee_token
def call_next(update, context):
    line_name = context.user_data.get("line_name")

    url = config['api_url'] + '/clerks/call-next'
    headers = {"Authorization": "Bearer " + context.user_data.get('token')}
    payload = {"line_name": line_name}

    res = requests.post(url, headers=headers, json=payload)

    if res.status_code == 409:
        keyboard = line_management_keyboard()
        update.message.reply_text("Line is empty.", reply_markup=keyboard)
        return CHOOSE_ACTION

    line_info = get_line_info(line_name)

    keyboard = line_management_keyboard()

    update.message.reply_text("Client '{}' was called.".format(line_info.get('current_client')))

    update.message.reply_text("You are now managing line '{}'.\n"
                              "Current client: {}.\n"
                              "People in line: {}.\n"
                              "Next client: {}.".format(
                                  line_name,
                                  line_info.get('current_client'),
                                  line_info.get('people_in_line'),
                                  line_info.get('next_client')
                              ),
                              reply_markup=keyboard)
    return CHOOSE_ACTION


def back(update, context):
    update.message.reply_text(
        "Choose an action:",
        reply_markup=main_keyboard)
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text('Line creation aborted.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


manage_lines_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(r"My lines 📋"), display_lines)],

    states={
        CHOOSE_LINE: [
            MessageHandler(Filters.regex(r"❌"), back),
            #MessageHandler(Filters.text, choose_line),
        ],
        CHOOSE_ACTION: [
            MessageHandler(Filters.regex(r"🔙"), display_lines),
            MessageHandler(Filters.regex(r"Refresh line info"), refresh_line_info),
            MessageHandler(Filters.regex(r"Call next"), call_next),
        ],
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
