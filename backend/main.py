from marshmallow import Schema, fields
from flask import Flask, request
from flask_restful import Resource, Api

import jwt
from functools import wraps

from firestore.tracks import Tracks
from firestore.users import Users

from external_apis.spotify import *
from external_apis.genius import *
from external_apis.news_api import *

from sparql.sparql import *

app = Flask(__name__)

api = Api(app)

basePath = '/api/v1'

tracks = Tracks(verbose=False)
users = Users(verbose=True)

spotify = Spotify(verbose=False)
genius = Genius(verbose=False)
newsapi = NewsAPI()
sparql = Sparql(verbose=False)


# ATTENTION! In order to secure API resources, environment variable
#            'FLASK_SECRET_KEY' must be defined first.
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        # print('Auth token received: ', token)
        if not token:
            return None, 401
        try:
            token = token.split()[1]
            decoded = jwt.decode(token, os.environ['FLASK_SECRET_KEY'], algorithms=["HS256"])
            print("Token decoded: ", decoded)
        except Exception as e:
            print(e)
            return None, 403
        return f(*args, **kwargs)
    return decorated


class RSearch(Resource):
    @token_required
    def get(self, query):
        if len(query) == 0 or len(query) > 255:
            return None, 400

        return_value = spotify.search(query)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


class RNews(Resource):
    @token_required
    def get(self, query):
        if len(query) == 0 or len(query) >= 255:
            return None, 400

        return_value = newsapi.get_news(q=query)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


# Function for BASE62 ID validation
def validate_base62_id(id):
    import base62
    try:
        if len(id) != 22:
            return False
        base62.decode(id)
        return True
    except Exception as e:
        print(e)
        return False


class RArtist(Resource):
    @token_required
    def get(self, artist_id):
        if validate_base62_id(artist_id) is False:
            return None, 400
        return_value = spotify.get_artist(artist_id)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


class RArtistAlbums(Resource):
    @token_required
    def get(self, artist_id):
        if validate_base62_id(artist_id) is False:
            return None, 400
        return_value = spotify.get_artist_albums(artist_id)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


class RArtistTopTracks(Resource):
    @token_required
    def get(self, artist_id):
        if validate_base62_id(artist_id) is False:
            return None, 400
        return_value = spotify.get_artist_top_tracks(artist_id)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


class RArtistGenius(Resource):
    @token_required
    def get(self, artist_id):
        if validate_base62_id(artist_id) is False:
            return None, 400
        spotify_artist = spotify.get_artist(artist_id)
        if spotify_artist is None:
            return None, 404
        artist_name = spotify_artist['name']
        return_value = genius.get_artist(artist_name=artist_name)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


class RArtistSparql(Resource):
    @token_required
    def get(self, artist_id):
        if validate_base62_id(artist_id) is False:
            return None, 400
        spotify_artist = spotify.get_artist(artist_id)
        if spotify_artist is None:
            return None, 404
        artist_name = spotify_artist['name']

        '''
        # Filtering italian artist if specified in Spotify's genres
        if len([i for i in spotify_artist['genres'] if 'italian' in i]) != 0:
            return_value = sparql.get_artist(artist_name=artist_name, language='it')
            # If it does not find anything we try searching english results.
            if return_value is None:
                return_value = sparql.get_artist(artist_name=artist_name)
        else:
            return_value = sparql.get_artist(artist_name=artist_name)'''
        language = request.args.get('language', default='en', type=str)
        get_full_info = request.args.get('get_full_info', default='false', type=str)
        if get_full_info == 'true':
            get_full_info = True
        else:
            get_full_info = False

        return_value = sparql.get_artist(
            artist_name=artist_name, language=language, get_full_info=get_full_info
        )

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


class RAlbum(Resource):
    @token_required
    def get(self, album_id):
        if validate_base62_id(album_id) is False:
            return None, 400
        return_value = spotify.get_album(album_id)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


class RAlbumTracks(Resource):
    @token_required
    def get(self, album_id):
        if validate_base62_id(album_id) is False:
            return None, 400
        return_value = spotify.get_album_tracks(album_id)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


class RAlbumGenius(Resource):
    @token_required
    def get(self, album_id):
        if validate_base62_id(album_id) is False:
            return None, 400
        spotify_album = spotify.get_album(album_id)
        if spotify_album is None:
            return None, 404
        artist_name = spotify_album['artists'][0]['name']
        album_name = spotify_album['name']
        return_value = genius.get_album(artist_name=artist_name, album_name=album_name)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


class RAlbumSparql(Resource):
    @token_required
    def get(self, album_id):
        if validate_base62_id(album_id) is False:
            return None, 400
        spotify_album = spotify.get_album(album_id)
        if spotify_album is None:
            return None, 404
        artist_name = spotify_album['artists'][0]['name']
        album_name = spotify_album['name']

        language = request.args.get('language', default='en', type=str)
        get_full_info = request.args.get('get_full_info', default='false', type=str)
        if get_full_info == 'true':
            get_full_info = True
        else:
            get_full_info = False

        return_value = sparql.get_album(
            artist_name=artist_name, album_name=album_name, language=language, get_full_info=get_full_info)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


# Class for Marshmallow TRACK_ID validation
class TrackSchema(Schema):
    lyrics = fields.Str(required=True)
    name = fields.Str(allow_none=True)


class RTrack(Resource):
    @token_required
    def get(self, track_id):
        if validate_base62_id(track_id) is False:
            return None, 400
        # Search track on Spotify
        return_value = spotify.get_track(track_id)
        if return_value is None:
            return None, 404
        else:
            # Search for available lyrics on Firestore DB
            track_db = tracks.get_track(track_id)
            if track_db:
                return_value['lyrics'] = track_db['lyrics']
            else:
                return_value['lyrics'] = None

            return return_value, 200

    @token_required
    def delete(self, track_id):
        if validate_base62_id(track_id) is False:
            return None, 400
        if tracks.get_track(track_id) is None:
            return None, 404
        return_value = tracks.delete_track(track_id=track_id)

        if return_value is None:
            return None, 500
        else:
            return None, 200

    def validate_body(self, json):
        try:
            return TrackSchema().load(data=json)
        except Exception as e:
            print(e)
            return False

    @token_required
    def post(self, track_id):
        if validate_base62_id(track_id) is False:
            return None, 400
        spotify_track = spotify.get_track(track_id)
        if spotify_track is None:
            return None, 404

        # Json validation
        try:
            json = request.get_json()
        except Exception as e:
            print("- Not valid JSON!")
            print(e)
            return None, 400

        body = self.validate_body(json)
        if body is False:
            print("- INVALID BODY RECEIVED!")
            return None, 400

        # Checking already existing track
        if tracks.get_track(track_id):
            print('- CONFLICT! This track is already saved in the database.')
            return None, 409

        print("- VALID BODY RECEIVED.", body)
        return_value = tracks.post_track(track_id, **body)

        if return_value:
            return None, 201
        return None, 500


class RTrackGenius(Resource):
    @token_required
    def get(self, track_id):
        if validate_base62_id(track_id) is False:
            return None, 400
        spotify_track = spotify.get_track(track_id)
        if spotify_track is None:
            return None, 404

        artist_name = spotify_track['artists'][0]['name']
        track_name = spotify_track['name']

        return_value = genius.get_track(artist_name=artist_name, track_name=track_name)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


class RTrackSparql(Resource):
    @token_required
    def get(self, track_id):
        if validate_base62_id(track_id) is False:
            return None, 400
        spotify_track = spotify.get_track(track_id)
        if spotify_track is None:
            return None, 404

        artist_name = spotify_track['artists'][0]['name']
        track_name = spotify_track['name']

        language = request.args.get('language', default='en', type=str)
        get_full_info = request.args.get('get_full_info', default='false', type=str)
        if get_full_info == 'true':
            get_full_info = True
        else:
            get_full_info = False

        return_value = sparql.get_track(
            artist_name=artist_name, track_name=track_name, language=language, get_full_info=get_full_info
        )

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


# Function for EMAIL validation
def validate_email(email):
    import re
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    try:
        if re.match(regex, email):
            return True
        return False
    except Exception as e:
        print(e)
        return False


# Class for Marshmallow USER validation
class UserSchema(Schema):
    provider = fields.Str(required=True, validate=lambda x: x in ['google', 'spotify'])
    name = fields.Str(allow_none=True)
    image = fields.Url(allow_none=True)


class RUser(Resource):
    @token_required
    def get(self, email):
        if validate_email(email) is False:
            return None, 400
        return_value = users.get_user(email=email)

        if return_value is None:
            return None, 500
        if len(return_value) == 0:
            return None, 404
        return return_value, 200

    @token_required
    def delete(self, email):
        if validate_email(email) is False:
            return None, 400
        if users.get_user(email) is None:
            return None, 404
        return_value = users.delete_user(email=email)

        if return_value is None:
            return None, 500
        else:
            return None, 200

    def validate_body(self, json):
        try:
            return UserSchema().load(data=json)
        except Exception as e:
            print(e)
            return False

    @token_required
    def post(self, email):
        if validate_email(email) is False:
            return None, 400
        # Json validation
        try:
            json = request.get_json()
        except Exception as e:
            print("- Not valid JSON!")
            print(e)
            return None, 400

        body = self.validate_body(json)
        if body is False:
            print("- INVALID BODY RECEIVED!")
            return None, 400

        # Checking already existing user
        if users.get_user(email):
            print('- CONFLICT! This user is already saved in the database.')
            return None, 409

        print("- VALID BODY RECEIVED: ", body)
        return_value = users.post_user(email, **body)

        if return_value:
            return None, 201
        return None, 500


class RUserFavoriteTracks(Resource):
    @token_required
    def get(self, email, track_id=None):
        if validate_email(email) is False or track_id is not None:
            return None, 400
        if users.get_user(email) is None:
            return None, 404
        return_value = users.get_favorite_tracks(email=email)

        if return_value is None:
            return None, 500
        else:
            return return_value, 200

    @token_required
    def delete(self, email, track_id):
        if validate_email(email) is False or validate_base62_id(track_id) is False:
            return None, 400
        if users.get_user(email) is None or spotify.get_track(track_id) is None:
            return None, 404

        return_value = users.delete_favorite_track(email=email, track_id=track_id)

        if return_value is None:
            return None, 500
        else:
            return None, 200

    @token_required
    def post(self, email, track_id):
        if validate_email(email) is False or validate_base62_id(track_id) is False:
            return None, 400
        if spotify.get_track(track_id) is None:
            return None, 404
        # Checking already existing favorite track
        if users.get_user(email):
            favorite_tracks = users.get_favorite_tracks(email=email)
            if favorite_tracks is not None:
                if track_id in favorite_tracks:
                    return None, 409
        else:
            return None, 404

        return_value = users.post_favorite_track(email=email, track_id=track_id)

        if return_value:
            return None, 201
        return None, 500


class RUserSpotify(Resource):
    @token_required
    def get(self):
        authorization_code = request.args.get('authorization_code')
        if not authorization_code:
            return None, 400
        return_value = spotify.get_user(authorization_code=authorization_code)

        if return_value is None:
            return None, 404
        else:
            return return_value, 200


api.add_resource(RSearch, f'{basePath}/search/<string:query>')

api.add_resource(RNews, f'{basePath}/news/<string:query>')

api.add_resource(RArtist, f'{basePath}/artists/<string:artist_id>')
api.add_resource(RArtistAlbums, f'{basePath}/artists/<string:artist_id>/albums')
api.add_resource(RArtistTopTracks, f'{basePath}/artists/<string:artist_id>/top-tracks')
api.add_resource(RArtistGenius, f'{basePath}/artists/<string:artist_id>/genius')
api.add_resource(RArtistSparql, f'{basePath}/artists/<string:artist_id>/sparql')

api.add_resource(RAlbum, f'{basePath}/albums/<string:album_id>')
api.add_resource(RAlbumTracks, f'{basePath}/albums/<string:album_id>/tracks')
api.add_resource(RAlbumGenius, f'{basePath}/albums/<string:album_id>/genius')
api.add_resource(RAlbumSparql, f'{basePath}/albums/<string:album_id>/sparql')

api.add_resource(RTrack, f'{basePath}/tracks/<string:track_id>')
api.add_resource(RTrackGenius, f'{basePath}/tracks/<string:track_id>/genius')
api.add_resource(RTrackSparql, f'{basePath}/tracks/<string:track_id>/sparql')

api.add_resource(RUser, f'{basePath}/users/<string:email>')
api.add_resource(
    RUserFavoriteTracks,
    f'{basePath}/users/<string:email>/favorite-tracks',
    f'{basePath}/users/<string:email>/favorite-tracks/<string:track_id>'
)
api.add_resource(RUserSpotify, f'{basePath}/users/spotify')


if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=5000, threaded=True, debug=True)
    app.run(host='127.0.0.1', port=5000, threaded=True, debug=False)
