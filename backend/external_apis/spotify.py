import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from requests.exceptions import ConnectionError, Timeout
from spotipy import SpotifyException
from spotipy.cache_handler import CacheHandler


class Spotify(object):
    def __init__(self, verbose=True):
        # ATTENTION! The following env variables must be setted first:
        #            "SPOTIPY_CLIENT_ID"; "SPOTIPY_CLIENT_SECRET"; "SPOTIPY_REDIRECT_URI"; "SPOTIPY_LOGIN_REDIRECT_URI"
        self.verbose = verbose
        self.spotify = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(cache_handler=MemoryCacheHandler()),
            requests_timeout=30,
            retries=10,
        )

    def search(self, query):
        if self.verbose:
            print(f"Searching on Spotify with QUERY: {query} ...")
        try:
            results = self.spotify.search(q=query, type='artist,album,track', limit=50)

            artists_results = results['artists']
            artists = artists_results['items']
            while artists_results['next'] and artists_results['offset'] < 50:
                artists_results = self.spotify.next(artists_results)['artists']
                artists.extend(artists_results['items'])
                
            albums_results = results['albums']
            albums = albums_results['items']
            while albums_results['next'] and albums_results['offset'] < 50:
                albums_results = self.spotify.next(albums_results)['albums']
                albums.extend(albums_results['items'])
                
            tracks_results = results['tracks']
            tracks = tracks_results['items']
            while tracks_results['next'] and tracks_results['offset'] < 50:
                tracks_results = self.spotify.next(tracks_results)['tracks']
                tracks.extend(tracks_results['items'])

            # Sorting artists and songs w.r.t popularity
            artists = sorted(artists, key=lambda x: x['popularity'], reverse=True)
            tracks = sorted(tracks, key=lambda x: x['popularity'], reverse=True)

            return {'artists': artists, 'albums': albums, 'tracks': tracks}

        except (KeyError, ValueError, SpotifyException, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_artist(self, artist_id):
        if self.verbose:
            print(f"Getting artist from Spotify with ARTIST_ID: {artist_id} ...")
        try:
            result = self.spotify.artist(artist_id=artist_id)
            return result
        except (ValueError, SpotifyException, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_album(self, album_id):
        if self.verbose:
            print(f"Getting album from Spotify with ALBUM_ID: {album_id} ...")
        try:
            result = self.spotify.album(album_id=album_id)
            return result

        except (ValueError, SpotifyException, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_artist_albums(self, artist_id):
        if self.verbose:
            print(f"Getting albums from Spotify by artist with ARTIST_ID: {artist_id} ...")
        try:
            results = self.spotify.artist_albums(artist_id=artist_id, album_type='album,single', limit=50)
            albums = results['items']
            while results['next'] and results['offset'] < 150:
                results = self.spotify.next(results)
                albums.extend(results['items'])
            return albums

        except (KeyError, ValueError, SpotifyException, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_artist_top_tracks(self, artist_id):
        if self.verbose:
            print(f"Getting top tracks from Spotify by artist with ARTIST_ID: {artist_id} ...")
        try:
            result = self.spotify.artist_top_tracks(artist_id=artist_id)
            top_tracks = result['tracks']
            return top_tracks

        except (KeyError, ValueError, SpotifyException, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_album_tracks(self, album_id):
        if self.verbose:
            print(f"Getting tracks from Spotify by ALBUM_ID: {album_id} ...")
        try:
            results = self.spotify.album_tracks(album_id=album_id, limit=50)
            tracks = results['items']
            while results['next'] and results['offset'] < 150:
                results = self.spotify.next(results)
                tracks.extend(results['items'])
            return tracks

        except (KeyError, ValueError, SpotifyException, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_track(self, track_id):
        if self.verbose:
            print(f"Getting track from Spotify with TRACK_ID: {track_id} ...")
        try:
            result = self.spotify.track(track_id=track_id)
            return result

        except (ValueError, SpotifyException, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_playlist_tracks(self, playlist_id, max_tracks=None):
        if self.verbose:
            print(f"Getting tracks from Spotify by playlist with PLAYLIST_ID: {playlist_id} ...")
        try:
            results = self.spotify.playlist_items(playlist_id=playlist_id)
            tracks = results['items']
            while results['next']:
                results = self.spotify.next(results)
                tracks.extend(results['items'])
            if max_tracks:
                if isinstance(max_tracks, int):
                    return tracks[:max_tracks]
            return tracks

        except (KeyError, ValueError, SpotifyException, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_user(self, authorization_code):
        if self.verbose:
            print(f"Getting user from Spotify with Spotify authorization code: {authorization_code} ...")
        try:
            import requests
            r = requests.post(
                url="https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "authorization_code",
                    "code": authorization_code,
                    "redirect_uri": os.environ['SPOTIPY_LOGIN_REDIRECT_URI'],
                    "client_id": os.environ['SPOTIPY_CLIENT_ID'],
                    "client_secret": os.environ['SPOTIPY_CLIENT_SECRET'],
                })
            token = r.json()
            if token:
                sp = spotipy.Spotify(auth=token['access_token'])
                user = sp.current_user()
                return user
            else:
                return None

        except (KeyError, ValueError, SpotifyException, ConnectionError, Timeout) as e:
            print(e)
            return None


class MemoryCacheHandler(CacheHandler):
    """
    A cache handler that simply stores the token info in memory as an
    instance attribute of this class. The token info will be lost when this
    instance is freed.
    """

    def __init__(self, token_info=None):
        """
        Parameters:
            * token_info: The token info to store in memory. Can be None.
        """
        self.token_info = token_info

    def get_cached_token(self):
        return self.token_info

    def save_token_to_cache(self, token_info):
        self.token_info = token_info