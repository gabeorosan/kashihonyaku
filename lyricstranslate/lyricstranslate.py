import json
import re
import urllib

import requests
from bs4 import BeautifulSoup

from lyricstranslate import ltutil
from lyricstranslate.song import Song
from lyricstranslate.node_error import NodeError
from lyricstranslate.search_result import SearchResult
from lyricstranslate.translation import Translation


class LyricsTranslate:
    # Get a Node from a node ID
    def node_from_id(self, nid):
        return self.node_from_url("https://lyricstranslate.com/en/node/" + str(nid) + "/view")

    # Get a Node from a URL
    def node_from_url(self, url):
        valid_url = re.compile(r"^(https?://(?:www\.)?lyricstranslate\.com)(?:/..)?/(.*)$")
        if not valid_url.fullmatch(url):
            raise NodeError("URL doesn't look like a LyricsTranslate URL")
        url = valid_url.sub(r"\1/en/\2", url)

        page = ltutil.soup_from_url(url)

        if 'node-type-song' in page.body['class']:
            lyrics = Song(page)
            return lyrics
        elif 'node-type-translation' in page.body['class']:
            translation = Translation(page)
            return translation
        else:
            raise NodeError("Unknown node type")

    # Searches content in the website, returning name, category and url for each result. It's based on the autocomplete
    # feature at the top of the LyricsTranslate page.
    def search(self, query):
        res = requests.get("https://lyricstranslate.com/en/ajax/lyricstranslategoogleautocomplete/autocomplete?query="
                           + urllib.parse.quote(query))
        res.raise_for_status()

        src_results = json.loads(res.text)['suggestions']
        if not src_results or not src_results[0]['value']:
            return []

        results = []
        for src_result in src_results:
            results.append(SearchResult(src_result['value'], src_result['data']['category'],
                                        "https://lyricstranslate.com" + src_result['data']['url']))

        return results

    # Get a node from a search result (obtained through LyricsTranslate.search())
    def node_from_search_result(self, result: SearchResult):
        return self.node_from_url(result.url)
