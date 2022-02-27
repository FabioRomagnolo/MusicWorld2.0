import os
from sparql.dbpedia import Dbpedia
from sparql.geonames import Geonames


class Sparql(object):
    def __init__(self, verbose=True, query_directory='sparql'):
        self.verbose = verbose
        self.query_directory = query_directory
        # Sparql classes
        self.dbpedia = Dbpedia(verbose=verbose, query_directory=self.query_directory)
        self.geonames = Geonames(verbose=verbose, query_directory=self.query_directory)

    def convert_dbpedia_to_wikipedia_urls(self, entity, excluded_keys=None):
        if excluded_keys is None:
            excluded_keys = []
        if entity is not None:
            for k, v in entity.items():
                if k in excluded_keys:
                    continue
                if isinstance(v, list):
                    entity[k] = self.dbpedia.get_wikipedia_urls(v)
                else:
                    entity[k] = self.dbpedia.get_wikipedia_urls([v])[0]
        return entity

    def get_artist(self, artist_name, language='en', get_full_info=False):
        dbpedia_artist = self.dbpedia.get_artist(artist_name, language, get_full_info)
        geonames_place = None
        if dbpedia_artist:
            hometown = dbpedia_artist.get('hometown', None)
            if hometown:
                geonames_place = self.geonames.get_place(hometown)

        # Let's convert all DBPedia urls to Wikipedia urls -> ATTENTION! It's a slow operation!
        # self.convert_dbpedia_to_wikipedia_urls(dbpedia_artist, excluded_keys='artist')

        artist = {'dbpedia': dbpedia_artist, 'geonames': geonames_place}
        return artist

    def get_album(self, artist_name, album_name, language='en', get_full_info=False):
        dbpedia_album = self.dbpedia.get_album(artist_name, album_name, language, get_full_info)
        geonames_place = None
        if dbpedia_album:
            hometown = dbpedia_album.get('hometown', None)
            if hometown:
                geonames_place = self.geonames.get_place(hometown)

        # Let's convert all DBPedia urls to Wikipedia urls -> ATTENTION! It's a slow operation!
        # self.convert_dbpedia_to_wikipedia_urls(dbpedia_album, excluded_keys='album')

        album = {'dbpedia': dbpedia_album, 'geonames': geonames_place}
        return album

    def get_track(self, artist_name, track_name, language='en', get_full_info=False):
        dbpedia_track = self.dbpedia.get_track(artist_name, track_name, language, get_full_info)
        geonames_place = None
        if dbpedia_track:
            hometown = dbpedia_track.get('hometown', None)
            if hometown:
                geonames_place = self.geonames.get_place(hometown)

        # Let's convert all DBPedia urls to Wikipedia urls -> ATTENTION! It's a slow operation!
        # self.convert_dbpedia_to_wikipedia_urls(dbpedia_track, excluded_keys='track')

        track = {'dbpedia': dbpedia_track, 'geonames': geonames_place}
        return track
