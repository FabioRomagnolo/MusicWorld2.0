from utils.query import simplify_research


def get_links(artist_name, track_name):
    query = f"{artist_name} {track_name}"
    query = simplify_research(query)
    query = query.replace(' ', '%20')

    links = []
    # Ultimate Guitar
    ug = {
        'title': 'Ultimate Guitar',
        'url': f'https://www.ultimate-guitar.com/search.php?search_type=title&value={query}',
        'description': 'Check tabs, chords and more.'
    }
    links.append(ug)
    # Songsterr
    songsterr = {
        'title': 'Songsterr',
        'url': f'https://www.songsterr.com/?pattern={query}',
        'description': 'Check tabs with rhythm.'
    }
    links.append(songsterr)
    # MuseScore
    musescore = {
        'title': 'MuseScore',
        'url': f'https://musescore.com/sheetmusic?text={query}',
        'description': 'Check piano scores.'
    }
    links.append(musescore)
    # YouTube
    youtube = {
        'title': 'YouTube',
        'url': f'https://www.youtube.com/results?search_query={query}%20tutorial',
        'description': 'Check video tutorials on YouTube.'
    }
    links.append(youtube)

    return links
