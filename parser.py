import bs4.element


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


def process_tag(tag):
    def span():
        text = process_tags(tag)

        if type(tag) is bs4.element.Tag and 'style' in tag.attrs:
            style = tag.attrs.get('style').strip().split(';')
            style = [list(map(lambda x: x.strip(), pair.split(':'))) for pair in style if pair]
            if style not in ([['text-decoration', 'underline']], [['text-align', 'justify']]):
                print('unusual style ' + str(style) + ' ' + str(tag))
            for key, value in style:
                if key == 'text-decoration':
                    if value == 'underline':
                        text = underline(text)
        return text

    def em():
        text = process_tags(tag)
        return italic(text)

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
            url = BASE_URL + url
        if url not in images:
            images.append(url)
        return ''

    def br():
        return '\n'

    def table():
        return process_tags(tag)

    def a():
        url = tag['href']
        if not url.startswith("http"):
            url = BASE_URL + url
        return link(''.join(process_tags(tag)), url)

    def script():
        print('javascript code ' + str(tag))
        return ' ' + code('javascript code')

    if type(tag) is not bs4.element.Tag:
        return tag

    try:
        return {
            'span': span,
            'p': p_div,
            'em': em,
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
        print(tag.name)
        return 'Ошибка'


def process_tags(tag):
    return ''.join(map(process_tag, tag.contents))


def find_process_tags(item, *args):
    global images
    images = []
    return process_tags(item.find(*args)), images


images = []
BASE_URL = 'https://mmcs.sfedu.ru'
