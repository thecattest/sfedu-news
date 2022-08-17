import bs4.element
from requests import get
from bs4 import BeautifulSoup
from get_logger import get_logger


def bold(text):
    return '<b>{}</b>'.format(text.strip())


def underline(text):
    return '<u>{}</u>'.format(text.strip())


def code(text):
    return '<code>{}</code>'.format(text.strip())


def link(text, url):
    return '<a href="{}">{}</a>'.format(url, text.strip())


def process_tag(tag):
    def span():
        text = process_tags(tag)

        if type(tag) is bs4.element.Tag and 'style' in tag.attrs:
            style = tag.attrs.get('style').strip().split(';')
            style = [list(map(lambda x: x.strip(), pair.split(':'))) for pair in style if pair]
            if style not in ([['text-decoration', 'underline']], [['text-align', 'justify']]):
                logger.info('unusual style ' + str(style) + ' ' + str(tag))
            for key, value in style:
                if key == 'text-decoration':
                    if value == 'underline':
                        text = underline(text)
        return text

    def p_div():
        return (span() + '\n') if tag.contents else ''

    def ol_ul():
        text = []
        for i, li in enumerate(filter(lambda x: type(x) is bs4.element.Tag, tag.contents)):
            item = (str(i+1) + '. ') if tag.name == 'ol' else '\u2022 '
            item += process_tags(li)
            text.append(item)
        return '\n'.join(text) + '\n'

    def strong():
        return bold(''.join(process_tags(tag)))

    def img():
        global images

        url = tag['src']
        if not url.startswith("http"):
            url = base_url + url
        if url not in images:
            images.append(url)
        return link('картинка' + (str(len(images)) if len(images) > 1 else ''), url) + '\n'

    def br():
        return '\n'

    def table():
        return process_tags(tag)

    def a():
        url = tag['href']
        if not url.startswith("http"):
            url = base_url + url
        return link(''.join(process_tags(tag)), url)

    def script():
        logger.info('javascript code ' + str(tag))
        return ' ' + code('javascript code')

    if type(tag) is not bs4.element.Tag:
        return tag

    try:
        return {
            'span': span,
            'p': p_div,
            'em': p_div,
            'div': p_div,
            'strong': strong,
            'img': img,
            'br': br,
            'a': a,
            'ol': ol_ul,
            'ul': ol_ul,
            'script': script,
            'table': table,
            'tbody': table,
            'tr': table,
            'td': table
        }.get(tag.name)()
    except TypeError:
        logger.error(tag.name)


def process_tags(tag):
    # return ''.join(filter(lambda x: len(x.strip()), map(process_tag, tag.contents)))
    return ''.join(map(process_tag, tag.contents))


def find_process_tags(item, *args):
    return process_tags(item.find(*args))


def get_soup_by_url(url):
    page = get(url)
    html = page.content.decode()
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_news_text(ind=1):
    global images

    images = []
    if ind < 1:
        return "Нумерация с единицы.", []
    start = ind // 9 * 9
    ind -= start
    current_news_url = news_url.format(start)
    soup = get_soup_by_url(current_news_url)
    news = list(filter(
        lambda x: type(x) is bs4.element.Tag and x['class'][0] != 'row-separator',
        soup.find('div', {'class': 'teaserarticles'})
    ))

    zero_news_item = soup.find('div', {'class': 'news_item_f'})
    news.insert(0, zero_news_item)
    news_item = news[ind]
    # print(news_item.prettify())

    read_on = news_item.find('a', {'class': 'readon'})
    if read_on is not None:
        news_item = get_soup_by_url(base_url + read_on['href']).find('div', {'class': 'news_item_a'})

    try:
        title = find_process_tags(news_item, 'h2', {'class': 'article_title'})
    except AttributeError:
        title = find_process_tags(news_item, 'h1', {'class': 'article_title'})
    try:
        try:
            date = find_process_tags(news_item, 'span', {'class': 'createdate'})
        except AttributeError:
            date = find_process_tags(news_item, 'span', {'class': 'modifydate'})
        create_by = find_process_tags(news_item, 'span', {'class': 'createby'})
        content = find_process_tags(news_item, 'div', {'class': 'newsitem_text'})

        text = '\n'.join([bold(title), code(date.strip()), code(create_by.strip()), content]).replace('\u200b', '')
        text = text.replace("\n\n\n\n\n", "\n\n").replace("\n\n\n\n", "\n\n").replace("\n\n\n", "\n\n")
        # print(text)
        return text, images
    except TypeError:
        logger.error('cannot parse something ' + str(start + ind))
        return 'Что-то неправильно парсится.', []


base_url = 'https://mmcs.sfedu.ru'
news_url = base_url + '/?start={}'

images = []
logger = get_logger('parser', 'mmcs_news_parser')

if __name__ == '__main__':
    print(get_news_text(1)[0])
