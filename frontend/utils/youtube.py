import urllib.request
import re
from utils.query import simplify_research, verify_result


def get_youtube_video_id(artist_name, track_name, verbose=False):
    query = f"{artist_name} {track_name}"
    query_simplified = simplify_research(query)

    query = query_simplified.replace(' ', '%20')
    try:
        url = u"https://www.youtube.com/results?search_query={}&gl=IT&hl=it".format(query).encode('ascii', 'ignore').decode('ascii')
        html_search = urllib.request.urlopen(url).read()
        video_ids = re.findall(r"watch\?v=(\S{11})", html_search.decode())
        video_id = video_ids[0]

        html_video = urllib.request.urlopen(f"https://www.youtube.com/watch?v={video_id}").read()
        title = str(html_video).split('<title>')[1].split('</title>')[0]

        if verbose:
            print('YOUTUBE VIDEO SEARCH - Track name used: ', query_simplified, 'Title of youtube video: ', title.lower())
        if verify_result(track_name, title) is True:
            return video_id
        else:
            return None
    except Exception as e:
        print(e)
        return None
