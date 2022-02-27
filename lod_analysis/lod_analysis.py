from utils.download import Download
from utils.evaluate import *

# Set the follow variables to execute specific actions only
ALLOW_DOWNLOAD = True
ALLOW_EVALUATE = True

# Set the playlist ID from which download data
# PLAYLIST - Rock: i classici (37i9dQZF1DWZNFWEuVbQpD)
# PLAYLIST - Modern Rock Hits (2oyJhb0BNwfDhI4Yrh4xp4)
# PLAYLIST - Modern Heavy Metal & Hard Rock Hits (49xcNMhndryLZ2XYmTMLy9)
# PLAYLIST - Top Rock Hits 00s 10s 20s (5Lwl3XaAOkEo4F9jXG1KK2)
# PLAYLIST - Pop & Rock Hits 2020s - 2010s - 2000s - 90s - 80s (64P8IcIYuKeZuk1D9pDDAF)
PLAYLIST_ID = "64P8IcIYuKeZuk1D9pDDAF"

# ATTENTION! This will determine the volume of analysis.
# - To take all the artists, albums and tracks from playlist set these to None.
MAX_TRACKS = 100
MAX_ALBUMS = 100
MAX_ARTISTS = 100

# ATTENTION! Setting this true will slow down the sparql queries!
GET_FULL_INFO = True

VERBOSE = True


if __name__ == '__main__':
    # ATTENTION! The following env variables must be setted first:
    # - GENIUS_TOKEN, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
    verbose = VERBOSE
    get_full_info = GET_FULL_INFO
    max_tracks = MAX_TRACKS
    max_albums = MAX_ALBUMS
    max_artists = MAX_ARTISTS
    download = Download(verbose=verbose)

    if ALLOW_DOWNLOAD:
        playlist_id = PLAYLIST_ID
        spotify_data = download.download_spotify_data_from_playlist(
            playlist_id=playlist_id, verbose=verbose,
            max_tracks=max_tracks, max_albums=max_albums, max_artists=max_artists
        )

        # DOWNLOAD ARTISTS, ALBUMS AND TRACKS DATA TO ANALYZE
        download.download_data(data=spotify_data, verbose=verbose, get_full_info=get_full_info)

    if ALLOW_EVALUATE:
        # EVALUATE ALL DATA FROM EXCELS DIRECTORY
        evaluate_data(verbose=verbose)
