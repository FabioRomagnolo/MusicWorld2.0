import os
import re

import lyricsgenius

from requests.exceptions import HTTPError, ConnectionError, Timeout
from utils.query import simplify_research


def clean_genius_lyrics(title, lyrics):
    lyrics = lyrics.replace(f"{title} Lyrics", "")
    lyrics = lyrics.replace(f"[Testo di \"{title}\"]\n\n", "")
    lyrics = lyrics.replace(f"[Letra de \"{title}\"]\n\n", "")
    lyrics = re.sub(r"\d+EmbedShare URLCopyEmbedCopy", "", lyrics)
    lyrics = re.sub(r"\d+Embed", "", lyrics)
    lyrics = re.sub(r"Embed", "", lyrics)
    return lyrics


def verify_result(query, result, exact_match=False):
    query, result = query.lower(), result.lower()
    if exact_match:
        return query == result
    else:
        if result.find('New Music Friday') != -1:
            return False
        for word in re.findall(r'\w+', query):
            if word in re.findall(r'\w+', result):
                return True
        return False


class Genius(object):
    def __init__(self, verbose=True):
        self.verbose = verbose
        # ATTENTION! In order to do authentication with token by public Genius API,
        #            'GENIUS_TOKEN' env variable must be setted.
        token = os.environ['GENIUS_TOKEN']
        self.genius = lyricsgenius.Genius(token, response_format='html', timeout=30)
        # Turning on status messages
        self.genius.verbose = verbose
        # Removing section headers (e.g. [Chorus]) from lyrics when searching
        # self.genius.remove_section_headers = True
        # Skipping hits thought to be non-songs (e.g. track lists)
        self.genius.skip_non_songs = True
        # Excluding songs with these words in their title
        # self.genius.excluded_terms = ["(Remix)", "(Live)"]

    def get_artist(self, artist_name):
        if self.verbose:
            print(f"Getting from Genius annotations about ARTIST: {artist_name} ...")
        try:
            research = self.genius.search_artists(
                search_term=artist_name, per_page=20, page=1
            )
            sections = research.get('sections', None)
            if sections is None:
                hits = research['hits']
            else:
                hits = research['sections'][0]['hits']
            if len(hits) == 0:
                return None
            else:
                # Let's take before the first result and verify
                searched_artist = hits[0]['result']
                if not searched_artist or verify_result(artist_name, searched_artist['name']) is False:
                    # Let's try with exact match if there are more possible results
                    for hit in hits:
                        possible_artist = hit['result']
                        if verify_result(artist_name, possible_artist['name'], exact_match=True):
                            searched_artist = possible_artist
                            break
            if not searched_artist or verify_result(artist_name, searched_artist['name']) is False:
                return None
            artist = self.genius.artist(artist_id=searched_artist['id'])

            # Get Genius URL
            url = artist['artist']['url']
            # Get description
            try:
                description = artist['artist']['description']['html']
            except (KeyError, ValueError, AttributeError):
                description = None
            # Get Akas
            try:
                alternate_names = artist['artist']['alternate_names']
            except (KeyError, ValueError, AttributeError):
                alternate_names = None

            return {'url': url,
                    'annotations': {'description': description, 'alternate_names': alternate_names}}

        except (HTTPError, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_album(self, artist_name, album_name):
        # Album research semplification
        album_name = simplify_research(album_name)

        if self.verbose:
            print(f"Getting from Genius annotations about ALBUM {album_name} by ARTIST {artist_name} ...")
        try:
            album_name = simplify_research(album_name)
            artist_name = simplify_research(artist_name)
            research = self.genius.search_albums(
                search_term=f"{album_name} {artist_name}", per_page=20, page=1
            )
            sections = research.get('sections', None)
            if sections is None:
                hits = research['hits']
            else:
                hits = research['sections'][0]['hits']
            if len(hits) == 0:
                return None
            else:
                # Let's take before the first result and verify
                searched_album = hits[0]['result']
                searched_artist = searched_album['artist']
                if not searched_album or verify_result(artist_name, searched_artist['name']) is False \
                        or verify_result(album_name, searched_album['name']) is False:
                    # Let's try with exact match if there are more possible results
                    for hit in hits:
                        possible_album = hit['result']
                        possible_artist = possible_album['artist']
                        if verify_result(album_name, possible_album['name'], exact_match=True) \
                                and verify_result(artist_name, possible_artist['name'], exact_match=True):
                            searched_album = possible_album
                            searched_artist = possible_artist
                            break
            if not searched_album or verify_result(artist_name, searched_artist['name']) is False \
                    or verify_result(album_name, searched_album['name']) is False:
                return None
            album = self.genius.album(album_id=searched_album['id'])

            # Get Genius URL
            url = album['album']['url']
            # Get description
            try:
                description = album['album']['description_annotation']['annotations'][0]['body']['html']
            except (KeyError, ValueError, AttributeError):
                description = None
            # Get producers, writers and labels names and links
            producers = []
            writers = []
            labels = []
            try:
                for sp in album['album']['song_performances']:
                    if sp['label'] == 'Producers':
                        for p in sp['artists']:
                            producers.append({'name': p['name'], 'url': p['url']})
                    if sp['label'] == 'Writers':
                        for w in sp['artists']:
                            writers.append({'name': w['name'], 'url': w['url']})
                    if sp['label'] == 'Label':
                        for l in sp['artists']:
                            labels.append({'name': l['name'], 'url': l['url']})
            except (KeyError, ValueError, AttributeError):
                writers = None
                producers = None
                labels = None

            return {'url': url,
                    'annotations': {'description': description, 'producers': producers, 'writers': writers, 'labels': labels}}

        except (HTTPError, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_track(self, artist_name, track_name):
        # Track research semplification
        track_name = simplify_research(track_name)
        if self.verbose:
            print(f"Getting from Genius lyrics and annotations about TRACK {track_name} by ARTIST {artist_name} ...")
        try:
            track_name = simplify_research(track_name)
            artist_name = simplify_research(artist_name)
            research = self.genius.search_songs(
                search_term=f"{track_name} {artist_name}", per_page=20, page=1
            )
            sections = research.get('sections', None)
            if sections is None:
                hits = research['hits']
            else:
                hits = research['sections'][0]['hits']
            if len(hits) == 0:
                return None
            else:
                # Let's take before the first result and verify
                searched_track = hits[0]['result']
                searched_artist = searched_track['primary_artist']
                if not searched_track or verify_result(artist_name, searched_artist['name']) is False \
                        or verify_result(track_name, searched_track['title']) is False:
                    # Let's try with exact match if there are more possible results
                    for hit in hits:
                        possible_track = hit['result']
                        possible_artist = possible_track['primary_artist']
                        if verify_result(track_name, possible_track['title'], exact_match=True)\
                                and verify_result(artist_name, possible_artist['name'], exact_match=True):
                            searched_track = possible_track
                            searched_artist = possible_artist
                            break
            if not searched_track or verify_result(artist_name, searched_artist['name']) is False \
                    or verify_result(track_name, searched_track['title']) is False:
                return None
            track = self.genius.song(searched_track['id'])
            # Get Genius URL
            url = track['song']['url']
            # Get lyrics
            lyrics = self.genius.lyrics(track['song']['id'])
            if lyrics:
                # Cleaning lyrics
                lyrics = clean_genius_lyrics(title=track['song']['title'], lyrics=lyrics)

            # Get description
            try:
                description = track['song']['description_annotation']['annotations'][0]['body']['html']
            except (KeyError, ValueError, AttributeError):
                description = None
            # Get producers names and links
            producers = []
            try:
                for p in track['song']['producer_artists']:
                    producers.append({'name': p['name'], 'url': p['url']})
            except (KeyError, ValueError, AttributeError):
                producers = None
            # Get writers names and links
            writers = []
            try:
                for w in track['song']['writer_artists']:
                    writers.append({'name': w['name'], 'url': w['url']})
            except (KeyError, ValueError, AttributeError):
                writers = None
            # Get labels
            labels = []
            try:
                for cp in track['song']['custom_performances']:
                    if cp['label'] == 'Label':
                        for l in cp['artists']:
                            labels.append({'name': l['name'], 'url': l['url']})
            except (KeyError, ValueError, AttributeError):
                labels = None

            return {'url': url, 'lyrics': lyrics,
                    'annotations': {'description': description, 'producers': producers, 'writers': writers, 'labels': labels}}

        except (HTTPError, ConnectionError, Timeout) as e:
            print(e)
            return None
