import ssl
import time

from SPARQLWrapper import SPARQLWrapper, JSON, POST, POSTDIRECTLY
from requests.exceptions import HTTPError, ConnectionError, Timeout
import os
from datetime import datetime
from sparql.utils import *


class Dbpedia(object):
    def __init__(self, verbose=True, query_directory='sparql'):
        self.verbose = verbose
        self.query_directory = query_directory
        # DBPEDIA Sparql Endpoint initialization
        self.endpoint = "https://dbpedia.org/sparql"
        self.sparql = SPARQLWrapper(self.endpoint)

        # Setting DBPedia default query parameters to fast up the queries
        self.sparql.addParameter("default-graph-uri", "http://dbpedia.org")
        self.sparql.addParameter('timeout', '30000')
        self.sparql.addParameter('signal_void', 'on')
        self.sparql.addParameter('signal_unconnected', 'on')

        self.sparql.setReturnFormat(JSON)
        # Alternative to very long URL encoded queries
        self.sparql.setRequestMethod(POSTDIRECTLY)
        self.sparql.setMethod(POST)

        # Workaround for ssl verification of sparql endpoint
        ssl._create_default_https_context = ssl._create_unverified_context

    def search(self, query):
        self.sparql.setQuery(query)
        if self.verbose:
            print(f"--- Query on {self.endpoint} ---\n{query}\n--- Getting results ---")

        try:
            results = self.sparql.queryAndConvert()
        except Exception:
            print("WARNING! An HTTP error occured. Sleeping and retrying request ...")
            # Sleeping a little and retrying ...
            time.sleep(2)
            try:
                results = self.sparql.queryAndConvert()
            except Exception as e:
                print(e)
                return [{}]

        for result in results["results"]["bindings"]:
            if self.verbose:
                print(result)
        if self.verbose:
            print('---------------------------')
        return results["results"]["bindings"]

    def get_wikipedia_urls(self, urls):
        """
            Method to retrieve from DBpedia's url the Wikipedia's page url.
            - If they're not valid DBpedia urls we don't mofify the input

            :param url: DBpedia resource's url.
            :return: Correspondent Wikipedia page's url or input url if it does not find anything.
        """
        if isinstance(urls, list):
            if all(isinstance(elem, str) for elem in urls):
                dbpedia_urls = []
                other_strings = []
                for u in urls:
                    if u.startswith('http://dbpedia.org/resource'):
                        dbpedia_urls.append('<'+u+'>')
                    else:
                        other_strings.append(u)
                # Setting query
                query = get_query_from_file("wikipedia_urls_query.txt")
                query = query.replace("DBPEDIA_URLS", ' '.join(dbpedia_urls))
                searched = self.search(query)
                wikipedia_urls = []
                for result in searched:
                    wikipedia_urls.append(result['entity_wiki']['value'])
                wikipedia_urls.extend(other_strings)

                if len(wikipedia_urls) != 0:
                    return wikipedia_urls
                else:
                    return urls
        return urls

    def get_artist(self, artist_name, language='en', get_full_info=False):
        if self.verbose:
            print(f"Getting from {self.endpoint} informations about ARTIST: {artist_name} ...")
        try:
            # Simplifying more research
            artist_name = simplify_research(artist_name)
            # Setting query
            if get_full_info:
                query_filename = os.path.join(self.query_directory, "artist_query_full.txt")
            else:
                query_filename = os.path.join(self.query_directory, "artist_query.txt")

            query = format_sparql_query(query_filename=query_filename, exact_match=False,
                                        language=language, artist_name=artist_name)

            searched = self.search(query)
            searched_artist = None
            if len(searched) != 0:
                searched_artist = searched[0]
            if not searched_artist:
                return None

            # Getting artist's fields
            artist = {}
            for k, v in searched_artist.items():
                value = get_values(v['value'])
                # Checking if is a particular string list: we need it as string only for certain variables.
                if isinstance(value, str):
                    if k not in ['artist', 'artist_name', 'wiki', 'birth_date', 'death_date',
                                 'start_year', 'end_year', 'hometown', 'abstract']:
                        if len(value) != 0:
                            value = value.split(', ')

                # Correcting start year's format string
                if k == 'start_year' or k == 'end_year':
                    value = value[0:4]

                # Correcting birth and death date's format string
                if k == 'birth_date' or k == 'death_date':
                    try:
                        datetime_object = datetime.strptime(value, '%Y-%m-%d')
                        value = datetime_object.strftime("%d %B %Y")
                    except Exception as e:
                        print(e)
                        value = ''

                artist[k] = value
                # Deleting entry if value is empty
                if artist[k] == '':
                    del artist[k]
            return artist

        except (HTTPError, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_album(self, artist_name, album_name, language='en', get_full_info=False):
        if self.verbose:
            print(f"Getting from {self.endpoint} informations about ALBUM: {album_name} by ARTIST {artist_name}...")
        try:
            # Simplifying more research
            artist_name = simplify_research(artist_name)
            album_name = simplify_research(album_name)
            # Setting query
            if get_full_info:
                query_filename = os.path.join(self.query_directory, "album_query_full.txt")
            else:
                query_filename = os.path.join(self.query_directory, "album_query.txt")

            query = format_sparql_query(query_filename=query_filename, exact_match=False,
                                        language=language, artist_name=artist_name, album_name=album_name)

            searched = self.search(query)
            searched_album = None
            if len(searched) != 0:
                if verify_dbpedia_url(searched[0]['album']['value'], album_name) is False:
                    # Disambiguating result with exact match
                    query = format_sparql_query(query_filename=query_filename, exact_match=True,
                                                language=language, artist_name=artist_name, album_name=album_name)
                    searched = self.search(query)
                    if len(searched) == 0:
                        return None
                searched_album = searched[0]
            if not searched_album:
                return None

            # Getting album's fields
            album = {}
            for k, v in searched_album.items():
                value = get_values(v['value'])
                # Checking if is a particular string list: we need it as string only for certain variables.
                if isinstance(value, str):
                    if k not in ['album', 'album_name', 'artist', 'artist_name',
                                 'wiki', 'hometown', 'released', 'abstract']:
                        if len(value) != 0:
                            value = value.split(', ')

                # Correcting release date's format string
                if k == 'released':
                    try:
                        datetime_object = datetime.strptime(value, '%Y-%m-%d')
                        value = datetime_object.strftime("%d %B %Y")
                    except Exception as e:
                        print(e)
                        value = ''

                album[k] = value
                # Deleting entry if value is empty
                if album[k] == '':
                    del album[k]
            return album

        except (HTTPError, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_track(self, artist_name, track_name, language='en', get_full_info=False):
        if self.verbose:
            print(f"Getting from {self.endpoint} informations about TRACK: {track_name} by ARTIST {artist_name}...")
        try:
            # Simplifying more research
            artist_name = simplify_research(artist_name)
            track_name = simplify_dbpedia_research(track_name)
            # Setting query
            if get_full_info:
                query_filename = os.path.join(self.query_directory, "track_query_full.txt")
            else:
                query_filename = os.path.join(self.query_directory, "track_query.txt")

            query = format_sparql_query(query_filename=query_filename, exact_match=False,
                                        language=language, artist_name=artist_name, track_name=track_name)

            searched = self.search(query)
            searched_track = None
            if len(searched) != 0:
                if verify_dbpedia_url(searched[0]['track']['value'], track_name) is False:
                    # Disambiguating result with exact match
                    query = format_sparql_query(query_filename=query_filename, exact_match=True,
                                                language=language, artist_name=artist_name, track_name=track_name)
                    searched = self.search(query)
                    if len(searched) == 0:
                        return None
                searched_track = searched[0]
            if not searched_track:
                return None

            # Getting track's fields
            track = {}
            for k, v in searched_track.items():
                value = get_values(v['value'])
                # Checking if is a particular string list: we need it as string only for certain variables.
                if isinstance(value, str):
                    if k not in ['track', 'track_name', 'artist', 'artist_name',
                                 'wiki', 'hometown', 'released', 'abstract']:
                        if len(value) != 0:
                            value = value.split(', ')

                # Correcting release date's format string
                if k == 'released':
                    try:
                        datetime_object = datetime.strptime(value, '%Y-%m-%d')
                        value = datetime_object.strftime("%d %B %Y")
                    except Exception as e:
                        print(e)
                        value = ''

                track[k] = value
                # Deleting entry if value is empty
                if track[k] == '':
                    del track[k]
            return track

        except (HTTPError, ConnectionError, Timeout) as e:
            print(e)
            return None
