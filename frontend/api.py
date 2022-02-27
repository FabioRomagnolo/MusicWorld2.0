import os
import jwt
import json
from json import JSONDecodeError
import requests


class Api(object):
    def __init__(self, verbose=True):
        # ATTENTION! In order to access backend resources a valid Json Web Token must be setted first
        self.token = jwt.encode({'user': 'Music World - Frontend'}, os.environ['FLASK_SECRET_KEY'], algorithm="HS256")
        self.verbose = verbose
        if self.verbose is True:
            print("--- JWT token setted for authorized requests: ", self.token)
        self.baseURL = os.environ.get('BACKEND_BASEURL', "http://127.0.0.1:5000/api/v1")

    def get(self, url, params=None, headers=None):
        if headers is not None:
            headers['Authorization'] = 'Bearer '+self.token
        else:
            headers = {'Authorization': 'Bearer '+self.token}
        r = requests.get(url=url, params=params, headers=headers)
        try:
            data = r.json()
        except (JSONDecodeError, ValueError):
            data = None
        if self.verbose:
            # print("--- GET STATUS CODE: ", r.status_code, r.text)
            print("--- GET STATUS CODE: ", r.status_code)
        return data

    def post(self, url, params=None, headers=None, data=None):
        if headers is not None:
            headers['Authorization'] = 'Bearer '+self.token
        else:
            headers = {'Authorization': 'Bearer '+self.token}
        r = requests.post(url=url, params=params, headers=headers, data=data)
        if self.verbose:
            print("--- POST STATUS CODE: ", r.status_code)
        return r.status_code

    def delete(self, url, params=None, headers=None):
        if headers is not None:
            headers['Authorization'] = 'Bearer ' + self.token
        else:
            headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.delete(url=url, params=params, headers=headers)
        if self.verbose:
            print("--- DELETE STATUS CODE: ", r.status_code)
        return r.status_code

    def search(self, query):
        try:
            # GET request
            URL = self.baseURL + "/search/" + query
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_news(self, query):
        try:
            # GET request
            URL = self.baseURL + "/news/" + query
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_artist(self, artist_id):
        try:
            # GET request
            URL = self.baseURL + "/artists/" + artist_id
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_artist_genius(self, artist_id):
        try:
            # GET request
            URL = self.baseURL + "/artists/" + artist_id + "/genius"
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_artist_sparql(self, artist_id, get_full_info=False):
        try:
            # GET request
            URL = self.baseURL + "/artists/" + artist_id + "/sparql"
            params = None
            if get_full_info is True:
                params = {'get_full_info': 'true'}
            return self.get(URL, params=params)
        except Exception as e:
            print(e)
            return None

    def get_artist_albums(self, artist_id):
        try:
            # GET request
            URL = self.baseURL + "/artists/" + artist_id + "/albums"
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_artist_top_tracks(self, artist_id):
        try:
            # GET request
            URL = self.baseURL + "/artists/" + artist_id + "/top-tracks"
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_album(self, album_id):
        try:
            # GET request
            URL = self.baseURL + "/albums/" + album_id
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_album_genius(self, album_id):
        try:
            # GET request
            URL = self.baseURL + "/albums/" + album_id + "/genius"
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_album_sparql(self, album_id, get_full_info=False):
        try:
            # GET request
            URL = self.baseURL + "/albums/" + album_id + "/sparql"
            params = None
            if get_full_info is True:
                params = {'get_full_info': 'true'}
            return self.get(URL, params=params)
        except Exception as e:
            print(e)
            return None

    def get_album_tracks(self, album_id):
        try:
            # GET request
            URL = self.baseURL + "/albums/" + album_id + "/tracks"
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_track(self, track_id):
        try:
            # GET request
            URL = self.baseURL + "/tracks/" + track_id
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_track_genius(self, track_id):
        try:
            # GET request
            URL = self.baseURL + "/tracks/" + track_id + "/genius"
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_track_sparql(self, track_id, get_full_info=False):
        try:
            # GET request
            URL = self.baseURL + "/tracks/" + track_id + "/sparql"
            params = None
            if get_full_info is True:
                params = {'get_full_info': 'true'}
            return self.get(URL, params=params)
        except Exception as e:
            print(e)
            return None

    def get_user(self, email):
        try:
            # GET request
            URL = self.baseURL + "/users/" + email
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def delete_user(self, email):
        try:
            # DELETE request
            URL = self.baseURL + "/users/" + email
            return self.delete(URL)
        except Exception as e:
            print(e)
            return None

    def post_user(self, email, provider, name, image):
        try:
            # POST request
            URL = self.baseURL + "/users/" + email
            headers = {'Content-type': 'application/json'}
            data = {
                'provider': provider,
                'name': name,
                'image': image
            }
            json_data = json.dumps(data)
            return self.post(url=URL, headers=headers, data=json_data)
        except Exception as e:
            print(e)
            return None

    def get_spotify_user(self, code):
        try:
            # GET request
            URL = self.baseURL + "/users/spotify"
            params = {'authorization_code': code}
            return self.get(url=URL, params=params)
        except Exception as e:
            print(e)
            return None

    def get_favorite_tracks(self, email):
        try:
            # GET request
            URL = self.baseURL + "/users/" + email + "/favorite-tracks"
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def add_favorite_track(self, email, track_id):
        try:
            # POST request
            URL = self.baseURL + "/users/" + email + "/favorite-tracks/" + track_id
            headers = {'Content-type': 'application/json'}
            data = {
                'track_id': track_id
            }
            return self.post(url=URL, headers=headers, data=data)
        except Exception as e:
            print(e)
            return None

    def remove_favorite_track(self, email, track_id):
        try:
            # DELETE request
            URL = self.baseURL + "/users/" + email + "/favorite-tracks/" + track_id
            return self.delete(URL)
        except Exception as e:
            print(e)
            return None
