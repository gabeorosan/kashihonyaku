# Implements the search results obtained through the LyricsTranslate.search() method
# from lyricstranslate.lyricstranslate import LyricsTranslate


class SearchResult:
    name = None
    category = None
    url = None

    def __init__(self, name, category, url):
        self.name = name
        self.category = category
        self.url = url

    def __str__(self):
        return self.category[:-1] + ': ' + self.name + ' - ' + self.url
