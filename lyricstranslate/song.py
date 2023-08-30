import html
import json
import re

import requests
from bs4 import BeautifulSoup

from lyricstranslate import ltutil
from lyricstranslate.node import Node
from lyricstranslate.node_error import NodeError


class Song(Node):
    def __init__(self, page: BeautifulSoup, translation_page=False):
        if page:
            self._page = page
        self._page = page

        self._translation_page = translation_page

        self._ajax_lyrics = False
        view_lyrics = self._page.select('div.view-lyrics')
        if not self._translation_page:
            self.nid = self._find_node_id()
        elif len(view_lyrics) != 0:
            # Sometimes, when the user is viewing a translation without being logged in,
            # original lyrics are unavailable until an AJAX request is made after clicking on a link.
            # Some other content is also hidden with the lyrics,
            # and the HTML representation of the title is also different.

            self._ajax_lyrics = True
            self.nid = view_lyrics[0]['nid']

            res = requests.post("https://lyricstranslate.com/en/callback/ltlyricsondemand/get/lyrics",
                                data={'nid': self.nid})
            res.raise_for_status()

            result = json.loads(res.text)
            if result['status'] != 1:
                raise NodeError("Couldn't get lyrics content: status was not 1 in the response")

            self._ajax_page = BeautifulSoup(result['data'], 'html.parser')
        else:
            # The lyrics are in a translation without AJAX, the nid must be found from some JavaScript via regex
            match = re.search(r"\"songnid\":\"([0-9]+)\"", str(self._page))
            if not match:
                raise NodeError("Couldn't find node id for lyrics")
            self.nid = match.group(1)

        self._submitter = None
        self._artist = None
        self._title = None
        self._language = None
        self._video = None
        self._content = None

    @property
    def submitter(self):
        if self._submitter is None:
            try:
                if self._ajax_lyrics:
                    self._submitter = self._ajax_page.select('div.authorsubmitted a')[0].text.strip()
                else:
                    self._submitter = self._page.select('div.song-node-text div.authorsubmitted a')[0].text.strip()
            except IndexError:
                raise NodeError("Couldn't find lyrics submitter")
        return self._submitter

    @property
    def artist(self):
        if self._artist is None:
            try:
                self._artist = self._page.select('div.song-node-info li.song-node-info-artist a')[0].decode_contents().strip()
            except IndexError:
                raise NodeError("Couldn't find lyrics artist")
        return self._artist

    @property
    def title(self):
        if self._title is None:
            try:
                if self._ajax_lyrics:
                    self._title = self._page.select('div.song-node-text h2.title-h2 span')[0].decode_contents().strip()
                else:
                    self._title = self._page.select('div.song-node-text h2.title-h2')[0].decode_contents().strip()
                if not self._title:
                    raise NodeError("Couldn't find lyrics title")
            except IndexError:
                raise NodeError("Couldn't find lyrics title")
        return self._title

    @property
    def language(self):
        if self._language is None:
            try:
                self._language = self._page.select('.langsmall-song div.mobile-hide')[0].decode_contents().strip()
                if not self._language:
                    raise NodeError("Couldn't find lyrics language")
            except IndexError:
                raise NodeError("Couldn't find lyrics language")
        return self._language

    @property
    def video(self):
        if self._video is None:
            try:
                video = self._page.select('div.youtube-player')[0]['data-id'].strip()
                if not video:
                    raise NodeError("Song video is present but couldn't retrieve it")
            except IndexError:
                return None
            self._video = {'type': 'youtube', 'id': video, 'url': f"https://youtu.be/{video}"}
        return self._video

    @property
    def content(self):
        if not self._content:
            if self._ajax_lyrics:
                paragraphs = self._ajax_page.select('div#song-body div.par')
            else:
                paragraphs = self._page.select('div.song-node-text div.par')

            self._content = ltutil.get_content(paragraphs)
        return self._content

    def __str__(self):
        out = "Type: lyrics\n"
        if self.nid:
            out += "Node ID: " + self.nid + '\n'
        out += "Submitter: " + self.submitter + '\n'
        out += "Artist: " + self.artist + '\n'
        out += "Title: " + self.title + '\n'
        out += "Language: " + self.language + '\n'
        if self.video:
            out += "Video: " + self.video['url'] + '\n'
        out += '\n'
        out += self.content

        return out
