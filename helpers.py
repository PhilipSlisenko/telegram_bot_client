import functools
import requests
import logging

from config import config


logger = logging.getLogger(__name__)


def guarantee_token(f):
    """ Guaranties that token is in context.user_data['token']. 
    Gets token from API if it is not already stored in context.user_data['token'] """
    @functools.wraps(f)
    def inner(update, context):

        if not context.user_data.get('token'):
            logger.info("There was no token")
            username = update.effective_user.full_name
            telegram_id = update.effective_user.id
            url = config['api_url'] + '/clients/authorize'
            payload = {
                "username": username,
                "password": str(username) + str(telegram_id),
                "telegram_id": telegram_id
            }
            res_json = requests.post(url, json=payload).json()
            context.user_data['token'] = res_json.get('token')
            context.user_data['username'] = username
        return f(update, context)

    return inner


def error(update, context):
    """Log Errors caused by Updates."""
    logger.exception('Update "%s" caused error "%s"', update, context.error)
