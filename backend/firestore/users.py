from google.cloud import firestore
from .delete_all_firestore import DeleteAllFirestore


class Users(object):
    def __init__(self, verbose=True):
        self.verbose = verbose
        # ATTENTION! 'GOOGLE_APPILCATION_CREDENTIALS' env variable must be setted.
        self.db = firestore.Client()
        self.delete_all_firestore = DeleteAllFirestore()

        # ----- Data model for USERS ----- #
        # "users"/"mario.rossi@gmail.com"
        self.provider = 'google'
        self.email = "mario.rossi@gmail.com"
        self.name = "Mario Rossi"
        self.image = 'https://lh3.googleusercontent.com/a-/AOh14 ... s96-c'
        # "favorite_tracks"/"Spotify_track_ID"
        self.favorite_tracks = []   # Collection of documents
        self.favorite_tracks.append({'48UPSzbZjgc449aqz8bxox': {'id': '48UPSzbZjgc449aqz8bxox'}})

    def get_user(self, email):
        if self.verbose:
            print(f"Getting user by EMAIL {email} ...")

        try:
            ref = self.db.collection('users').document(f'{email}').get()
            if ref.exists:
                return ref.to_dict()
            if self.verbose:
                print(f"User with EMAIL {email} not found!")
            return {}
        except (ValueError, ConnectionError, TimeoutError) as e:
            print(e)
            return None

    def delete_user(self, email):
        if self.verbose:
            print(f"Deleting user with EMAIL {email} ...")

        try:
            ref = self.db.collection('users').document(f'{email}').get()
            if ref.exists:
                # self.db.collection('users').document(f'{email}').delete()
                # Deleting all data belonging to user
                self.delete_all_firestore.delete_document(self.db.collection('users').document(f'{email}'))
                return email
            if self.verbose:
                print(f"User with EMAIL {email} not found!")
            return None
        except (ValueError, ConnectionError, TimeoutError) as e:
            print(e)
            return None

    def post_user(self, email, **kwargs):
        if self.verbose:
            print(f"Posting user account with EMAIL {email}\nand DATA: {kwargs.values()}...")

        try:
            ref = self.db.collection('users').document(f'{email}')
            ref.set({
                'email': email,
                'name': kwargs.get('name'),
                'image': kwargs.get('image'),
                'provider': kwargs.get('provider')
            })
            return email
        except (ValueError, ConnectionError, TimeoutError) as e:
            print(e)
            return None

    def get_favorite_tracks(self, email):
        if self.verbose:
            print(f"Getting user's favorite tracks by EMAIL {email} ...")

        try:
            fav_tracks = []
            ref = self.db.collection('users').document(f'{email}').collection('favorite_tracks')
            docs = ref.stream()
            for doc in docs:
                fav_tracks.append(doc.to_dict())
            if len(fav_tracks) > 0:
                return fav_tracks
            else:
                if self.verbose:
                    print(f"No favorite tracks found for user {email}!")
                return []
        except (ValueError, ConnectionError, TimeoutError) as e:
            print(e)
            return None

    def delete_favorite_track(self, email, track_id):
        if self.verbose:
            print(f"Deleting favorite track {track_id} by user with EMAIL {email} ...")

        try:
            ref = self.db.collection('users').document(f'{email}')\
                .collection('favorite_tracks').document(f'{track_id}').get()
            if ref.exists:
                self.db.collection('users').document(f'{email}')\
                    .collection('favorite_tracks').document(f'{track_id}').delete()
                return track_id
            if self.verbose:
                print(f"User with EMAIL {email} and FAVORITE TRACK {track_id} not found!")
            return None
        except (ValueError, ConnectionError, TimeoutError) as e:
            print(e)
            return None

    def post_favorite_track(self, email, track_id):
        if self.verbose:
            print(f"Posting user's favorite track {track_id} on account with EMAIL {email}...")

        try:
            ref = self.db.collection('users').document(f'{email}')\
                .collection('favorite_tracks').document(f'{track_id}')
            ref.set({
                'id': track_id
            })
            return track_id
        except (ValueError, ConnectionError, TimeoutError) as e:
            print(e)
            return None
