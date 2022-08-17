from telegram import Bot
from telegram import ParseMode, InputMediaPhoto
from telegram.error import BadRequest

from get_logger import get_logger
from parser import get_news_text


try:
    with open('tg_config') as f:
        TOKEN = f.readline()
except FileNotFoundError:
    raise FileNotFoundError('Telegram config file not found')


def get_news(ind):
    logger.info('check')
    text, images = get_news_text(ind)

    try:
        with open('last_sent.txt') as f:
            last_sent = f.read()
        if last_sent == text + '\n'.join(images):
            bot.send_message(THECATTEST, "nothing new")
            return
    except FileNotFoundError:
        pass

    if len(images) == 1:
        try:
            bot.send_photo(CHANNEL, images[0], text, parse_mode=ParseMode.HTML)
        except BadRequest:
            bot.send_photo(CHANNEL, images[0])
            bot.send_message(CHANNEL, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    elif len(images) > 1:
        media = [InputMediaPhoto(url) for url in images[:10]]
        bot.send_media_group(CHANNEL, media)
    else:
        bot.send_message(CHANNEL, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    with open('last_sent.txt', 'wt') as f:
        f.write(text + '\n'.join(images))


CHANNEL = -1001754457370
THECATTEST = 888848705

bot = Bot(TOKEN)
logger = get_logger('bot', 'mmcs_news_bot')

get_news(1)
