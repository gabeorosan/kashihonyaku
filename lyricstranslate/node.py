import re

from lyricstranslate.node_error import NodeError


# Abstract class for the Node concept of LyricsTranslate. A Node can be anything (song, translation, collection, etc.).
class Node:
    _page = None
    nid = None

    def _find_node_id(self):
        for body_class in self._page.body['class']:
            if re.fullmatch(r"page-node-([0-9]+)", body_class):
                return body_class[10:]
        raise NodeError("Couldn't find node ID")
