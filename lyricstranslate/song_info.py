from bs4 import BeautifulSoup

from lyricstranslate.node_error import NodeError


class SongInfo:
    def __init__(self, page: BeautifulSoup):
        self._page = page

        self._artist = None
        self._featuring_artists = None
        self._other_performances = None
        self._title = None
        self._languages = None
        self._translations = None
        self._translation_requests = None
        self._video = None

    @property
    def artist(self):
        if not self._artist:
            try:
                self._artist = self._page.select('div.song-node-info li.song-node-info-artist a')[0]\
                    .decode_contents().strip()
            except IndexError:
                raise NodeError("Couldn't find lyrics artist")
        return self._artist

    def _get_artist_list(self, beginning: str):
        artists = self._page.select('div.song-node-info li.song-node-info-artist.song-info-2')
        if len(artists) == 0:
            return []
        else:
            for found in artists:
                if found.text.startswith(beginning):
                    artist_list_unstripped = found.text.split(':')[1].split(',')
                    artist_list = []
                    for artist in artist_list_unstripped:
                        artist_list.append(artist.strip())
                    return artist_list

    @property
    def featuring_artists(self):
        if self._featuring_artists is None:
            self._featuring_artists = self._get_artist_list("Featuring artists:")
        return self._featuring_artists

    @property
    def other_performances(self):
        if self._other_performances is None:
            self._other_performances = self._get_artist_list("Also performed by:")
        return self._other_performances

    @property
    def title(self):
        if self._title is None:
            try:
                self._title = self._page.select('div.song-node-text h2.title-h2')[0].text.strip()
            except IndexError:
                raise NodeError("Couldn't get title of song")
        return self._title

    @property
    def languages(self):
        if self._languages is None:
            try:
                languages_container = self._page.select('.langsmall-song div.mobile-hide')[0]
                found = languages_container.select('#translit-tab-original')
                if found:
                    languages = found.text
                else:
                    languages = languages_container.text
                languages_list = languages.split(',')
                self._languages = []
                for language in languages_list:
                    self._languages.append(language.strip())
            except IndexError:
                raise NodeError("Couldn't get language list of song")

        return self._languages

    '''@property
    def translations(self):
        if self._translations is None:
            try:
    '''
