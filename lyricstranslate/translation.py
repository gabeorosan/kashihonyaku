import json
import re

import requests
from bs4 import BeautifulSoup

from lyricstranslate import ltutil
from lyricstranslate.song import Song
from lyricstranslate.node import Node
from lyricstranslate.node_error import NodeError
from lyricstranslate.song_info import SongInfo


class Translation(Node):
    def __init__(self, page: BeautifulSoup):
        self._page = page

        self.nid = self._find_node_id()
        self.song_nid = self._find_song_nid()

        # Find out if lyrics are directly available on the page or they need a new request
        self.has_lyrics = len(self._page.select('div.view-lyrics')) == 0
        self._lyrics = None

        self._song = None

        self._song_info = None
        self._submitter = None
        self._title = None
        self._language = None
        self._language_ids = None
        self._comments = None
        self._content = None

    @property
    def song_info(self):
        if self._song_info is None:
            self._song_info = SongInfo(self._page)
        return self._song_info

    def _find_song_nid(self):
        # It can be found in some weird javascript at the end of the page
        match = re.search(r"\"songnid\":\"([0-9]+)\"", str(self._page))
        if not match:
            raise NodeError("Couldn't find node id for lyrics")
        self.nid = match.group(1)

    @property
    def submitter(self):
        if self._submitter is None:
            try:
                self._submitter = self._page.select('div.translate-node-text div.authorsubmitted a')[0].text.strip()
                if not self._submitter:
                    raise NodeError("Couldn't find translation submitter")
            except IndexError:
                raise NodeError("Couldn't find translation submitter")
        return self._submitter

    @property
    def title(self):
        if self._title is None:
            try:
                self._title = self._page.select('div.translate-node-text h2.title-h2')[0].decode_contents().strip()
                if not self._title:
                    raise NodeError("Couldn't find translation title")
            except IndexError:
                raise NodeError("Couldn't find translation title")
        return self._title

    @property
    def language(self):
        if self._language is None:
            try:
                self._language = self._page.select('div.langsmall-song span.mobile-hide')[0].decode_contents().rsplit(' ', 1)[0]
                if not self._language:
                    raise NodeError("Couldn't find translation language")
            except IndexError:
                raise NodeError("Couldn't find translation language")
        return self._language

    @property
    def language_ids(self):
        if self._language_ids is None:
            try:
                translate_node_text = self._page.select('div.translate-node-text')[0]
                if translate_node_text.has_attr('lang'):
                    translation_id = translate_node_text['lang']
                else:
                    translation_id = 'en'

                song_node_text = self._page.select('div.song-node-text')[0]
                if song_node_text.has_attr('lang'):
                    song_id = song_node_text['lang']
                else:
                    song_id = 'en'
            except IndexError:
                raise NodeError("Couldn't find language ids")

            self._language_ids = {
                'translation': translation_id,
                'song': song_id
            }
        return self._language_ids

    @property
    def content(self):
        if self._content is None:
            paragraphs = self._page.select('div.translate-node-text div.par')
            self._content = ltutil.get_content(paragraphs)
        return self._content

    @property
    def lyrics(self):
        if not self._lyrics:
            if self.has_lyrics:
                paragraphs = self._page.select('div.song-node-text div.par')
                self._lyrics = ltutil.get_content(paragraphs)
            else:
                res = requests.post("https://lyricstranslate.com/en/callback/ltlyricsondemand/get/lyrics",
                                    data={'nid': self.nid})
                res.raise_for_status()

                result = json.loads(res.text)
                if result['status'] != 1:
                    raise NodeError("Couldn't get lyrics content: status was not 1 in the response")

                lyrics_page = BeautifulSoup(result['data'], 'html.parser')

                paragraphs = lyrics_page.select('div#song-body div.par')
                self._lyrics = ltutil.get_content(paragraphs)

        return self._lyrics

    @property
    def song(self):
        if not self._song:
            self._song = Song(ltutil.soup_from_url(f"https://lyricstranslate.com/en/node/{self.song_info['nid']}/view"))
        return self._song

    def __str__(self):
        out = "Type: translation\n"
        if self.nid:
            out += "Node ID: " + self.nid + '\n'
        out += "Submitter: " + self.submitter + '\n'
        out += "Title: " + self.title + '\n'
        out += "Language: " + self.language + '\n'
        out += "Language IDs: " + self.language_ids['song'] + ">" + self.language_ids['translation'] + '\n'
        out += '\n'
        out += self.content

        return out
