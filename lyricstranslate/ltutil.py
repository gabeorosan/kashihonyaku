import html

import bs4
import requests

from lyricstranslate.node_error import NodeError


def soup_from_url(url: str) -> bs4.BeautifulSoup:
    res = requests.get(url)
    res.raise_for_status()

    return bs4.BeautifulSoup(res.text, 'html.parser')


def get_content(paragraphs: bs4.ResultSet):
    content = ''
    for paragraph in paragraphs:
        lines = paragraph.find_all('div')
        for line in lines:
            content += html.unescape(line.decode_contents().strip()) + '\n'
        content += '\n'
    if not content:
        raise NodeError("Couldn't find translation content")

    return content[:-2]
