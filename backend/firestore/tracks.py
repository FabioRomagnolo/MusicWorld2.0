from google.cloud import firestore


class Tracks(object):
    def __init__(self, verbose=True):
        self.verbose = verbose
        # ATTENTION! 'GOOGLE_APPILCATION_CREDENTIALS' env variable must be setted.
        self.db = firestore.Client()

        # ----- Data model for TRACKS ----- #
        # "tracks"/"Spotify_track_ID"
        self.id = '48UPSzbZjgc449aqz8bxox'
        self.name = 'Californication'
        self.lyrics = "Very long text"

    def get_track(self, track_id):
        if self.verbose:
            print(f"Getting track {track_id} from Firestore DB...")

        try:
            ref = self.db.collection('tracks').document(f'{track_id}').get()
            if ref.exists:
                return ref.to_dict()
            if self.verbose:
                print(f"Track with TRACK_ID {track_id} not found!")
            return None
        except (ValueError, ConnectionError, TimeoutError) as e:
            print(e)
            return None

    def delete_track(self, track_id):
        if self.verbose:
            print(f"Deleting track with TRACK_ID {track_id} ...")

        try:
            ref = self.db.collection('tracks').document(f'{track_id}').get()
            if ref.exists:
                self.db.collection('tracks').document(f'{track_id}').delete()
                return track_id
            if self.verbose:
                print(f"Track with TRACK_ID {track_id} not found!")
            return None
        except (ValueError, ConnectionError, TimeoutError) as e:
            print(e)
            return None

    def post_track(self, track_id, **kwargs):
        if self.verbose:
            print(f"Posting track with TRACK_ID {track_id}\nand DATA: {kwargs.values()}...")

        try:
            ref = self.db.collection('tracks').document(f'{track_id}')
            ref.set({
                'id': track_id,
                'name': kwargs.get('name'),
                'lyrics': kwargs.get('lyrics'),
            })
            return track_id
        except (ValueError, ConnectionError, TimeoutError) as e:
            print(e)
            return None
