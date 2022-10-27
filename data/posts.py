import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin

from re import search


def bold(text):
    return '<b>{}</b>'.format(text.strip())


def underline(text):
    return '<u>{}</u>'.format(text.strip())


def italic(text):
    return '<i>{}</i>'.format(text.strip())


def code(text):
    return '<code>{}</code>'.format(text.strip())


def link(text, url):
    return '<a href="{}">{}</a>'.format(url, text.strip())


class Post(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    message_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    def get_text(self):
        title = link(bold(self.title), self.link)
        date_string = code(self.datetime.strftime('%d.%m.%Y %H:%M'))
        author = code(self.author)
        text = '\n'.join([title, date_string, author, '\n' + self.text])
        return text

    @staticmethod
    def shorten_link(link):
        return search(r'https://mmcs.sfedu.ru/(.+/)*\d{4,}', link).group()

    def __repr__(self):
        return f"<Post {self.id} {self.title} >"
