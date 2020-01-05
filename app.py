import logging

from telegram.ext import Updater

from config import config
import handlers
import helpers
import conversations

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO
                    )
logger = logging.getLogger(__name__)


token = config['bot_token']
updater = Updater(token=token, use_context=True)

dispatcher = updater.dispatcher


dispatcher.add_handler(handlers.start_handler)

dispatcher.add_handler(handlers.other_handler)

dispatcher.add_handler(handlers.test_handler)


dispatcher.add_handler(conversations.join_line_conversation_handler)

dispatcher.add_handler(conversations.manage_lines_conversation_handler)

dispatcher.add_error_handler(helpers.error)

updater.start_polling()
# updater.idle()
