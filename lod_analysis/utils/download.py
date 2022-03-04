from backend.external_apis.spotify import *
from backend.external_apis.genius import *
from backend.sparql.sparql import *
import os
import time
import random

from utils.excel import save_excel


class Download(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

        self.spotify = Spotify()
        self.genius = Genius(verbose=False)
        self.dbpedia = Dbpedia(verbose=False, query_directory=os.path.join('../../frontend', 'backend', 'sparql'))
        self.geonames = Geonames(verbose=False, query_directory=os.path.join('../../frontend', 'backend', 'sparql'))

    def download_spotify_data_from_playlist(self, playlist_id, verbose=True,
                                            max_artists=None, max_albums=None, max_tracks=None):
        if verbose:
            if max_tracks:
                print(f"Getting MAXIMUM {max_artists} artists, {max_albums} albums, {max_tracks} tracks "
                      f"from playlist with PLAYLIST ID {playlist_id}")
            else:
                print(f"Getting ALL tracks from playlist with PLAYLIST ID {playlist_id}")
        results = self.spotify.get_playlist_tracks(playlist_id=playlist_id)

        tracks = []
        artists = []
        albums = []
        for result in results:
            for artist in result['track']['artists']:
                artists.append(
                    {'artist_id': artist['id'], 'artist_name': artist['name']}
                )
            albums.append({
                'album_id': result['track']['album']['id'], 'album_name': result['track']['album']['name'],
                'artist_id': result['track']['artists'][0]['id'], 'artist_name': result['track']['artists'][0]['name']
            })
            tracks.append({
                'track_id': result['track']['id'], 'track_name': result['track']['name'],
                'artist_id': result['track']['artists'][0]['id'], 'artist_name': result['track']['artists'][0]['name']
            })
        tracks = remove_duplicated_dictionaries_from_list(tracks)
        albums = remove_duplicated_dictionaries_from_list(albums)
        artists = remove_duplicated_dictionaries_from_list(artists)

        if max_tracks:
            tracks = random.sample(tracks, max_tracks)
            # tracks = tracks[:max_tracks]
        if max_albums:
            albums = random.sample(albums, max_albums)
            # albums = albums[:max_albums]
        if max_artists:
            artists = random.sample(artists, max_artists)
            # artists = artists[:max_artists]

        return_value = {
            'artists': artists,
            'albums': albums,
            'tracks': tracks
        }
        return return_value

    def download_data(self, data, get_full_info=False, verbose=True):
        # DOWNLOAD ARTISTS DATA
        data['artists'] = self.download_artists(data['artists'], get_full_info=get_full_info, verbose=verbose)
        save_excel(data['artists'], filename='artists', get_full_info=get_full_info, verbose=verbose)
        if verbose:
            print("----------- ARTISTS DOWNLOAD COMPLETED SUCCESSFULLY! -----------")

        # DOWNLOAD ALBUMS DATA
        data['albums'] = self.download_albums(data['albums'], get_full_info=get_full_info, verbose=verbose)
        save_excel(data['albums'], filename='albums', get_full_info=get_full_info, verbose=verbose)
        if verbose:
            print("----------- ALBUMS DOWNLOAD COMPLETED SUCCESSFULLY! -----------")

        # DOWNLOAD TRACKS DATA
        data['tracks'] = self.download_tracks(data['tracks'], get_full_info=get_full_info, verbose=verbose)
        save_excel(data['tracks'], filename='tracks', get_full_info=get_full_info, verbose=verbose)
        if verbose:
            print("----------- TRACKS DOWNLOAD COMPLETED SUCCESSFULLY! -----------")
        return data

    def download_artist_data(self, artist_name, get_full_info=False):
        data = {}
        start_time = time.time()
        dbpedia = self.dbpedia.get_artist(artist_name=artist_name, get_full_info=get_full_info)
        dbpedia_download_time = time.time() - start_time

        start_time = time.time()
        geonames = None
        if dbpedia:
            hometown = dbpedia.get('hometown', None)
            if hometown:
                geonames = self.geonames.get_place(hometown)
        geonames_download_time = time.time() - start_time

        start_time = time.time()
        genius = self.genius.get_artist(artist_name=artist_name)
        genius_download_time = time.time() - start_time
        data.update({
            'genius': genius,
            'dbpedia': dbpedia,
            'geonames': geonames,
            'genius_download_time': genius_download_time,
            'dbpedia_download_time': dbpedia_download_time,
            'geonames_download_time': geonames_download_time
        })
        return data

    def download_album_data(self, artist_name, album_name, get_full_info=False):
        data = {}
        start_time = time.time()
        dbpedia = self.dbpedia.get_album(
                artist_name=artist_name, album_name=album_name, get_full_info=get_full_info
            )
        dbpedia_download_time = time.time() - start_time

        start_time = time.time()
        geonames = None
        if dbpedia:
            hometown = dbpedia.get('hometown', None)
            if hometown:
                geonames = self.geonames.get_place(hometown)
        geonames_download_time = time.time() - start_time

        start_time = time.time()
        genius = self.genius.get_album(artist_name=artist_name, album_name=album_name)
        genius_download_time = time.time() - start_time

        data.update({
            'genius': genius,
            'dbpedia': dbpedia,
            'geonames': geonames,
            'genius_download_time': genius_download_time,
            'dbpedia_download_time': dbpedia_download_time,
            'geonames_download_time': geonames_download_time
        })
        return data

    def download_track_data(self, artist_name, track_name, get_full_info=False):
        data = {}
        start_time = time.time()
        dbpedia = self.dbpedia.get_track(
                artist_name=artist_name, track_name=track_name, get_full_info=get_full_info
            )
        dbpedia_download_time = time.time() - start_time

        start_time = time.time()
        geonames = None
        if dbpedia:
            hometown = dbpedia.get('hometown', None)
            if hometown:
                geonames = self.geonames.get_place(hometown)
        geonames_download_time = time.time() - start_time

        start_time = time.time()
        genius = self.genius.get_track(artist_name=artist_name, track_name=track_name)
        genius_download_time = time.time() - start_time
        data.update({
            'genius': genius,
            'dbpedia': dbpedia,
            'geonames': geonames,
            'genius_download_time': genius_download_time,
            'dbpedia_download_time': dbpedia_download_time,
            'geonames_download_time': geonames_download_time
        })
        return data

    def download_artists(self, artists, get_full_info=False, verbose=True):
        if verbose:
            print(f"----------- DOWNLOADING DATA ABOUT {len(artists)} ARTISTS -----------")
        for i, ar in enumerate(artists):
            if verbose:
                print(f"- {i+1}. Downloading artist's data: {ar['artist_name']} ...")
            ar.update(self.download_artist_data(artist_name=ar['artist_name'], get_full_info=get_full_info))
        return artists

    def download_albums(self, albums, get_full_info=False, verbose=True):
        if verbose:
            print(f"----------- DOWNLOADING DATA ABOUT {len(albums)} ALBUMS -----------")
        for i, al in enumerate(albums):
            if verbose:
                print(f"- {i+1}. Downloading album's data: {al['album_name']} by {al['artist_name']} ...")
            al.update(self.download_album_data(artist_name=al['artist_name'], album_name=al['album_name'], get_full_info=get_full_info))
        return albums

    def download_tracks(self, tracks, get_full_info=False, verbose=True):
        if verbose:
            print(f"----------- DOWNLOADING DATA ABOUT {len(tracks)} TRACKS -----------")
        for i, t in enumerate(tracks):
            if verbose:
                print(f"- {i+1}. Downloading track's data: {t['track_name']} by {t['artist_name']} ...")
            t.update(self.download_track_data(artist_name=t['artist_name'], track_name=t['track_name'], get_full_info=get_full_info))
        return tracks


def remove_duplicated_dictionaries_from_list(l):
    seen = set()
    new_l = []
    for d in l:
        t = tuple(sorted(d.items()))
        if t not in seen:
            seen.add(t)
            new_l.append(d)
    return new_l
