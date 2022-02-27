from SPARQLWrapper import SPARQLWrapper, JSON
from requests.exceptions import HTTPError, ConnectionError, Timeout
import os
from sparql.utils import get_query_from_file, get_values


class Geonames(object):
    def __init__(self, verbose=True, query_directory='sparql'):
        self.verbose = verbose
        self.query_directory = query_directory
        # GEONAMES Sparql Endpoint initialization
        self.endpoint = "http://factforge.net/repositories/ff-news"
        self.sparql = SPARQLWrapper(self.endpoint)
        self.sparql.setReturnFormat(JSON)

    def search(self, query):
        self.sparql.setQuery(query)
        if self.verbose:
            print(f"--- Query on {self.endpoint} ---\n{query}\n--- Getting results ---")
        results = self.sparql.query().convert()

        for result in results["results"]["bindings"]:
            if self.verbose:
                print(result)
        if self.verbose:
            print('---------------------------')
        return results["results"]["bindings"]

    def get_place(self, dbpedia_resource_uri):
        """
        Function to get the Geonames' place informations through linked DBpedia data.

        :param dbpedia_resource_uri: URI of DBpedia resource to link on.
        :return: Geonames' data about place
        """
        if self.verbose:
            print(f"Getting from {self.endpoint} informations about PLACE: {dbpedia_resource_uri} ...")
        try:
            # Setting query
            query = get_query_from_file(os.path.join(self.query_directory, "place_query.txt"))
            query = query.replace("DBPEDIA_RESOURCE_URI", dbpedia_resource_uri)

            searched = self.search(query)
            searched_place = None
            if len(searched) != 0:
                searched_place = searched[0]
            if not searched_place:
                return None

            # Getting place's fields
            place = {}
            for k, v in searched_place.items():
                place[k] = get_values(v['value'])
            return place

        except (HTTPError, ConnectionError, Timeout) as e:
            print(e)
            return None
