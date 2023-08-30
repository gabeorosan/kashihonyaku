from flask import Flask, render_template, request, jsonify
import requests
import urllib

import requests
from bs4 import BeautifulSoup

from lyricstranslate import ltutil
from lyricstranslate.song import Song
from lyricstranslate.node_error import NodeError
from lyricstranslate.search_result import SearchResult
from lyricstranslate.translation import Translation
from lyricstranslate import LyricsTranslate
from lyricstranslate.node_error import NodeError
import re

def get_autocomplete_results(query):
    url = f"https://lyricstranslate.com/en/ajax/lyricstranslategoogleautocomplete/autocomplete?query={query}"
    headers = {
        "User-Agent": "Mozilla/5.0"  # Some websites require a User-Agent header to be set
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an exception for HTTP error responses
        x = response.json()
        return [song['value'] for song in x['suggestions']][:5]
    except requests.RequestException as e:
        print(f"An error occurred while making the request: {e}")
        return []
    

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
        
def get_lyrics(query, search=True, with_lyrics=False, only_lyrics=False):
    lt = LyricsTranslate()
    results_list = []

    try:
        if search:
            results = lt.search(query)
            if len(results) == 0:
                return "No results"
            else:
                for result in results:
                    results_list.append(str(result))
                return results_list
        else:
            node = lt.node_from_url(query)
            if with_lyrics or only_lyrics:
                if 'lyrics' not in node.__dict__ or node.lyrics is None:
                    return "No lyrics"
                else:
                    results_list.append(str(node.lyrics))
            elif not only_lyrics:
                results_list.append(str(node))
            return results_list

    except NodeError as e:
        return f"Error while retrieving node: {e}"


def extract_info(results):
    data = []
    for result in results:
        # Use regular expressions to extract relevant info
        match = re.match(r'(\w+): (.*?) - (.*?) - (https://lyricstranslate\.com/.*)', result)
        if match:
            data.append({
                'Type': match.group(1),
                'Artist': match.group(2),
                'Title': match.group(3),
                'URL': match.group(4)
            })
    return data

def get_all_lyrics(query):
    results = get_lyrics(query, search=True, with_lyrics=True)
    # Sample usage
    extracted_data = extract_info(results)
    url = extracted_data[0]['URL']
    valid_url = re.compile(r"^(https?://(?:www\.)?lyricstranslate\.com)(?:/..)?/(.*)$")
    if not valid_url.fullmatch(url):
        raise NodeError("URL doesn't look like a LyricsTranslate URL")
    url = valid_url.sub(r"\1/en/\2", url)

    page = ltutil.soup_from_url(url)
    lyrics = Song(page)
    #print(lyrics.content.split('\n'))
    lang_id = {o.string: o['value'] for o in page.select('optgroup option')}
    fid = lyrics.nid
    video_id = lyrics.video
    lang_lyr = {'original': lyrics.content, 'video': video_id}
    for l in lang_id:

        url = 'https://lyricstranslate.com/en/callback/getlyrics'
        payload = {
            'id': lang_id[l],
            'fid': fid,
        }

        try:
            response = requests.post(url, data=payload)
            data = response.json()

            # Extract the 'body' field and parse it using BeautifulSoup
            soup = BeautifulSoup(data['body'], 'html.parser')
            pars = soup.select('div.par')

            # Extract the text from each div and join them

            ly = ltutil.get_content(pars)
            print('succ')
            lang_lyr[l] = ly
        except requests.RequestException as e:
                print(f"An error occurred while making the request: {e}")
    return lang_lyr

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_song():
    query = request.json.get('query', '')
    results = get_autocomplete_results(query)
    return jsonify(results=results)

@app.route('/lyrics', methods=['POST'])
def search_lyrics():
    song = request.json.get('query', '')
    results = get_all_lyrics(song)
    return jsonify(results=results)

if __name__ == '__main__':
    app.run(debug=True)

'''

def get_autocomplete_results(query):
    
    url = f"https://lyricstranslate.com/en/ajax/lyricstranslategoogleautocomplete/autocomplete?query={query}"
    headers = {
        "User-Agent": "Mozilla/5.0"  # Some websites require a User-Agent header to be set
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an exception for HTTP error responses
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred while making the request: {e}")
        return []
'''