from parser import find_process_tags, BASE_URL, bold, code, link

from bs4 import BeautifulSoup
from feedparser import parse
from datetime import datetime as dt
from time import mktime

from telegram import Bot
from telegram import ParseMode, InputMediaPhoto
from telegram.error import BadRequest

from db_init import db_session, Post


try:
    with open('tg_config') as f:
        TOKEN = f.readline().strip()
except FileNotFoundError:
    raise FileNotFoundError('Telegram config file not found')

# CHANNEL = -1001754457370
TEST_CHANNEL = -1001885344884
THECATTEST = 888848705
bot = Bot(TOKEN)


def refresh():
    feed_url = BASE_URL + '/?format=feed&type=rss&start=1'
    feed = parse(feed_url)
    db = db_session.create_session()
    for item in reversed(feed.entries):
        post, images = get_post(item)
        db_post = db.query(Post).filter(Post.title == post.title).first()
        if db_post:
            keys = ('title', 'text', 'datetime')
            if db_post.to_dict(only=keys) != post.to_dict(keys):
                print("delete and post")
                delete_post(db_post)
                db.delete(db_post)
                db.commit()
                message_id = send_post(post, images).message_id
                post.message_id = message_id
                db.add(post)
                db.commit()
        else:
            print("new")
            message = send_post(post, images)
            post.message_id = message.message_id
            db.add(post)
            db.commit()
    db.close()


def send_post(post, images):
    text = post.get_text()
    if len(images) == 1:
        try:
            return bot.send_photo(TEST_CHANNEL, images[0], text, parse_mode=ParseMode.HTML)
        except BadRequest:
            bot.send_photo(TEST_CHANNEL, images[0])
            return bot.send_message(TEST_CHANNEL, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    elif len(images) > 1:
        media = [InputMediaPhoto(url) for url in images[:10]]
        bot.send_media_group(TEST_CHANNEL, media)
        return bot.send_message(TEST_CHANNEL, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        return bot.send_message(TEST_CHANNEL, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def edit_post(post, images):
    if len(images) == 1:
        bot.edit_message_caption(chat_id=TEST_CHANNEL, message_id=post.message_id,
                                 caption=post.get_text(), parse_mode=ParseMode.HTML)
    else:
        bot.edit_message_text(chat_id=TEST_CHANNEL, message_id=post.message_id,
                              text=post.get_text(), parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def delete_post(post):
    bot.delete_message(TEST_CHANNEL, message_id=post.message_id)


def get_post(item):
    html = BeautifulSoup(item.summary, 'html.parser')

    text, images = find_process_tags(html, 'div', {'class': 'feed-description'})
    text = text.replace(' @sfedu', '@sfedu').strip()

    post = Post()
    post.title = item.title
    post.datetime = dt.fromtimestamp(mktime(item.published_parsed))
    post.link = item.link
    post.author = item.author_detail['name']
    post.text = text

    return post, images


if __name__ == '__main__':
    refresh()
