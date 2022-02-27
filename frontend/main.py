import os

from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from wtforms import Form, StringField, SubmitField, validators
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests

from models import User
from api import Api

from utils.links import get_links
from utils.html import format_genius_html
from utils.youtube import get_youtube_video_id

app = Flask(__name__)
# Setting the secret key to have full access on Flask session.
app.secret_key = os.environ['FLASK_SECRET_KEY']

# Adding jinja2 extensions
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

api = Api(verbose=True)


@app.template_filter('strftime')
def _jinja2_filter_datetime(str, precision, format):
    if str is None:
        return None
    date = None
    if precision == 'year':
        date = datetime.strptime(str, '%Y')
    if precision == 'month':
        date = datetime.strptime(str, '%Y-%m')
    if precision == 'day':
        date = datetime.strptime(str, '%Y-%m-%d')
    if precision == 'millisecond':
        ms = int(str)
        date = datetime.fromtimestamp(ms/1000.0)
    if precision == 'news_utc':
        date = datetime.strptime(str, "%Y-%m-%dT%H:%M:%SZ")
    try:
        retval = date.strftime(format)
    except Exception as e:
        print(e)
        retval = date.strftime('%Y')
    return retval


@app.template_filter('format')
def _jinja2_filter_number(number):
    return "{:0,}".format(number)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404
app.register_error_handler(404, page_not_found)


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500
app.register_error_handler(500, internal_server_error)


@app.route('/', methods=['GET', 'POST'])
def index():
    context = {}

    class SearchForm(Form):
        query = StringField('query', [validators.Length(min=1, max=255)])
        submit = SubmitField(label='Submit')

    user = session.get('user', None)
    title = 'Music World | Songs, lyrics, facts & more'
    form = SearchForm()
    context.update({'user': user, 'title': title, 'form': form})

    if user:
        # Getting favorite tracks ids in order to check if also this track is a favorite one
        favorite_tracks_ids = []
        favorite_tracks_db = api.get_favorite_tracks(email=user['email'])
        if favorite_tracks_db:
            for t in favorite_tracks_db:
                favorite_tracks_ids.append(t['id'])
        context.update({'favorite_tracks_ids': favorite_tracks_ids})

    if request.method == 'GET':
        return render_template('index.html', **context)

    if request.method == 'POST':
        query = request.form['query']
        retval = api.search(query)

        if retval:
            artists, albums, tracks = retval.get('artists', None), retval.get('albums', None), retval.get('tracks', None)
            if artists or albums or tracks:
                context.update({
                    'artists': artists, 'albums': albums, 'tracks': tracks, 'query': query, 'retval': retval
                })
            else:
                context.update({'error': 'No artist, album or track found with that name!'})
        else:
            context.update({'error': 'There is a connection issue with the backend main server. '
                                     'If the problem persists, please contact us.'})

        return render_template('index.html', **context)


@app.route('/artists/<artist_id>/genius/', methods=['GET'])
def artist_genius(artist_id):
    context = {}
    genius = api.get_artist_genius(artist_id)
    if genius is not None:
        genius_url = genius.get('url', None)
        context.update({'genius_url': genius_url})

        genius_annotations = genius.get('annotations', None)
        if genius_annotations:
            genius_alternate_names = genius_annotations.get('alternate_names', None)
            genius_description = format_genius_html(genius_annotations.get('description', None))
            context.update({
                'genius_alternate_names': genius_alternate_names, 'genius_description': genius_description,
            })
    return render_template('extensions/genius.html', **context)


@app.route('/artists/<artist_id>/sparql/', methods=['GET'])
def artist_sparql(artist_id):
    sparql = api.get_artist_sparql(artist_id, get_full_info=False)
    if sparql is not None:
        dbpedia = sparql.get('dbpedia', None)
        geonames = sparql.get('geonames', None)
        context = {'dbpedia': dbpedia, 'geonames': geonames}
        return render_template('extensions/sparql.html', **context)


@app.route('/artists/<artist_id>', methods=['GET'])
def artist(artist_id):
    context = {}

    artist = api.get_artist(artist_id)
    if not artist:
        return render_template('error/404.html'), 404
    user = session.get('user', None)
    title = f"Music World | {artist['name']}"

    context.update({
        'user': user, 'title': title, 'artist': artist
    })

    if user:
        # Getting favorite tracks ids in order to check if also this track is a favorite one
        favorite_tracks_ids = []
        favorite_tracks_db = api.get_favorite_tracks(email=user['email'])
        if favorite_tracks_db:
            for t in favorite_tracks_db:
                favorite_tracks_ids.append(t['id'])
        context.update({'favorite_tracks_ids': favorite_tracks_ids})

    albums = api.get_artist_albums(artist_id)

    # Albums filtering - Taking only UNIQUE singles and albums
    def filter_albums(albums):
        from utils.query import simplify_research
        import difflib
        filtered = []

        # Creating a list of groups of too similar album names
        grouped_similar_album_names = []
        for a in albums:
            if any(simplify_research(a['name']) in g for g in grouped_similar_album_names):
                continue
            else:
                grouped_similar_album_names.append(difflib.get_close_matches(
                    simplify_research(a['name']), [simplify_research(al['name']) for al in albums], cutoff=0.9))
        # Taking only first album for each group of similar albums
        for g in grouped_similar_album_names:
            for a in albums:
                if simplify_research(a['name']) == g[0]:
                    filtered.append(a)
                    break
        return filtered

    albums = filter_albums(albums)
    top_tracks = api.get_artist_top_tracks(artist_id)

    # news = api.get_news(query=f"\"{artist['name']}\"+(music OR musica)")
    # context.update({'news': news})

    links = get_links(artist_name=artist['name'], track_name="")
    context.update({
        'albums': albums, 'top_tracks': top_tracks, 'links': links
    })

    return render_template('artist.html', **context)


@app.route('/albums/<album_id>/genius/', methods=['GET'])
def album_genius(album_id):
    context = {}

    genius = api.get_album_genius(album_id)
    if genius:
        genius_url = genius.get('url', None)
        context.update({'genius_url': genius_url})

        genius_annotations = genius.get('annotations', None)
        if genius_annotations:
            genius_description = format_genius_html(genius_annotations.get('description', None))
            genius_producers = genius_annotations.get('producers', None)
            genius_writers = genius_annotations.get('writers', None)
            genius_labels = genius_annotations.get('labels')

            context.update({
                'genius_description': genius_description, 'genius_producers': genius_producers,
                'genius_writers': genius_writers, 'genius_labels': genius_labels
            })
    return render_template('extensions/genius.html', **context)


@app.route('/albums/<album_id>/sparql/', methods=['GET'])
def album_sparql(album_id):
    sparql = api.get_album_sparql(album_id, get_full_info=False)
    if sparql is not None:
        dbpedia = sparql.get('dbpedia', None)
        geonames = sparql.get('geonames', None)
        context = {'dbpedia': dbpedia, 'geonames': geonames}
        return render_template('extensions/sparql.html', **context)


@app.route('/albums/<album_id>', methods=['GET'])
def album(album_id):
    context = {}

    album = api.get_album(album_id)
    if not album:
        return render_template('error/404.html'), 404
    user = session.get('user', None)
    title = f"Music World | {album['name']}"
    tracks = api.get_album_tracks(album_id)

    context.update({
        'user': user, 'title': title, 'album': album, 'tracks': tracks
    })

    if user:
        # Getting favorite tracks ids in order to check if also this track is a favorite one
        favorite_tracks_ids = []
        favorite_tracks_db = api.get_favorite_tracks(email=user['email'])
        if favorite_tracks_db:
            for t in favorite_tracks_db:
                favorite_tracks_ids.append(t['id'])
        context.update({'favorite_tracks_ids': favorite_tracks_ids})

    artist_name, album_name = album['artists'][0]['name'], album['name']

    # news = api.get_news(query=f"\"{artist_name}\"+(music OR musica)")
    # context.update({'news': news})

    links = get_links(artist_name, album_name)
    context.update({'links': links})

    return render_template('album.html', **context)


@app.route('/tracks/<track_id>/genius/', methods=['GET'])
def track_genius(track_id):
    context = {}

    user = session.get('user', None)
    context.update({'user': user})

    genius = api.get_track_genius(track_id)
    if genius:
        genius_url = genius.get('url', None)
        context.update({'genius_url': genius_url})

        genius_annotations = genius.get('annotations', None)
        if genius_annotations:
            genius_lyrics = genius.get('lyrics', None)

            genius_description = format_genius_html(genius_annotations.get('description', None))
            genius_producers = genius_annotations.get('producers', None)
            genius_writers = genius_annotations.get('writers', None)
            genius_labels = genius_annotations.get('labels', None)

            context.update({
                'genius_lyrics': genius_lyrics, 'genius_description': genius_description,
                'genius_producers': genius_producers, 'genius_writers': genius_writers,
                'genius_labels': genius_labels
            })
    return render_template('extensions/genius.html', **context)


@app.route('/tracks/<track_id>/sparql/', methods=['GET'])
def track_sparql(track_id):
    sparql = api.get_track_sparql(track_id, get_full_info=False)
    if sparql is not None:
        dbpedia = sparql.get('dbpedia', None)
        geonames = sparql.get('geonames', None)
        context = {'dbpedia': dbpedia, 'geonames': geonames}
        return render_template('extensions/sparql.html', **context)


@app.route('/tracks/<track_id>', methods=['GET', 'POST', 'DELETE'])
def track(track_id):
    context = {}

    user = session.get('user', None)
    context.update({'user': user})

    if request.method == 'GET':
        track = api.get_track(track_id)
        if not track:
            return render_template('error/404.html'), 404
        title = f"Music World | {track['name']}"
        context.update({'title': title, 'track': track})

        if user:
            # Getting favorite tracks ids in order to check if also this track is a favorite one
            favorite_tracks_ids = []
            favorite_tracks_db = api.get_favorite_tracks(email=user['email'])
            if favorite_tracks_db:
                for t in favorite_tracks_db:
                    favorite_tracks_ids.append(t['id'])

            context.update({'favorite_tracks_ids': favorite_tracks_ids})

        artist_name, track_name = track['artists'][0]['name'], track['name']

        video = get_youtube_video_id(artist_name, track_name)
        links = get_links(artist_name, track_name)
        context.update({
            'video': video, 'links': links
        })

        # news = api.get_news(query=f"\"{artist_name}\"+(music OR musica)")
        # context.update({'news': news})

        return render_template('track.html', **context)

    if request.method == 'POST':
        if user is not None:
            print('--- Adding new favorite track')
            api.add_favorite_track(user['email'], track_id)
        return redirect(request.referrer, code=303)

    if request.method == 'DELETE':
        if user is not None:
            print('--- Removing track from favorites')
            api.remove_favorite_track(user['email'], track_id)
        return redirect(request.referrer, code=303)


@app.route('/login', methods=['GET', 'POST'])
def login():
    context = {}

    # ATTENTION! In order to do Google or Spotify authentication, 'GOOGLE_OAUTH_CLIENT_ID'
    #            and 'SPOTIFY_OAUTH_CLIENT_ID' env variables must be setted.
    context.update({'google_signin_client_id': os.environ['GOOGLE_OAUTH_CLIENT_ID']})
    context.update({'spotify_signin_client_id': os.environ['SPOTIFY_OAUTH_CLIENT_ID']})

    user = session.get('user', None)
    if user:
        return redirect(url_for('profile'))

    title = 'Music World | Login with Google or Spotify'
    context.update({'title': title})

    if request.method == 'GET':
        if 'error' in request.args.keys():
            context.update({'error': request.args['error']})

        if 'code' in request.args.keys() and 'error' not in request.args.keys():
            # Spotify authentication
            data = api.get_spotify_user(request.args['code'])
            print('--- Login data received: ', data)
            try:
                email = data['email']
                name = data['display_name']
                if data['images']:
                    image = data['images'][0]['url']
                else:
                    image = None
                user = User(provider='spotify', email=email, name=name, image=image)

                user_db = user.get()
                if user_db is not None:
                    session['user'] = user_db
                    print(f"--- Login successful with Spotify account: {email}")
                    return redirect(url_for('profile'))
                else:
                    error = "Can't login with the Spotify account! Maybe you've already registered " \
                            "this email with a Google account."
                    context.update({'error': error})
                    print(error)

            except Exception as e:
                error = "Can't login with the Spotify account! Maybe there's a connection issue with Spotify, but " \
                        "if the problem persists, please contact us."
                context.update({'error': error})
                print(e)
                print(error)

        return render_template('login.html', **context)

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            print('--- Login data received: ', data)
            # Google authentication
            if data['provider'] == 'google':
                try:
                    token = data['token']
                    email = data['email']
                    name = data['name']
                    image = data['image']

                    # Specify the CLIENT_ID of the app that accesses the backend:
                    CLIENT_ID = os.environ['GOOGLE_OAUTH_CLIENT_ID']
                    idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
                    # ID token is valid. Get the user's Google Account ID from the decoded token.
                    userid = idinfo['sub']
                    user = User(provider='google', email=email, name=name, image=image)

                    user_db = user.get()
                    if user_db is not None:
                        session['user'] = user_db
                        print(f"--- Login successful with Google account: {email}")
                        return redirect(url_for('profile'), code=303)
                    else:
                        error = "Can't login with the Google account! Maybe you've already registered " \
                                "this email with a Spotify account."
                        context.update({'error': error})
                        print(error)

                except Exception as e:
                    error = "Can't login with the Google account! Maybe there's a connection issue with Google, but " \
                            "if the problem persists, please contact us."
                    context.update({'error': error})
                    print(e)
                    print(error)
        else:
            error = "Invalid format of user's data"
            context.update({'error': error})

        return redirect(url_for('login', error=context.get('error', None)), code=303)


@app.route('/profile', methods=['GET', 'DELETE'])
def profile():
    context = {}

    # ATTENTION! In order to do Google or Spotify authentication, 'GOOGLE_OAUTH_CLIENT_ID'
    #            and 'SPOTIFY_OAUTH_CLIENT_ID' env variables must be setted.
    context.update({'google_signin_client_id': os.environ['GOOGLE_OAUTH_CLIENT_ID']})
    context.update({'spotify_signin_client_id': os.environ['SPOTIFY_OAUTH_CLIENT_ID']})

    user = session.get('user', None)
    if user is None:
        error = "Can't access to profile page! Try to login again, but " \
                "if the problem persists please contact us."
        return redirect(url_for('login', error=error), code=303)

    title = f"Music World | Profile of {user['name']}"
    context.update({'user': user, 'title': title})

    if request.method == 'GET':
        print("Current user: ", user)

        favorite_tracks, favorite_tracks_ids = [], []
        favorite_tracks_db = api.get_favorite_tracks(email=user['email'])
        if favorite_tracks_db is not None:
            for t in favorite_tracks_db:
                favorite_tracks.append(api.get_track(t['id']))
                favorite_tracks_ids.append(t['id'])

        context.update({'favorite_tracks': favorite_tracks, 'favorite_tracks_ids': favorite_tracks_ids})

        return render_template('profile.html', **context)

    if request.method == 'DELETE':
        api.delete_user(user['email'])
        return redirect(url_for('login'), code=303)


@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        # Remove the current user from the session if it is there
        session.pop('user', None)
        print('--- User logged out.')
        return redirect(url_for('index'), code=303)

if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=8080, threaded=True, debug=True)
    app.run(host='127.0.0.1', port=8080, threaded=True, debug=False)
