import re
from utils.query import simplify_research


def get_query_from_file(filename):
    query = ""
    try:
        with open(filename, 'r') as file:
            query = file.read().replace('\n', '')
    except OSError as e:
        print(e)
    return query


def get_values(string, separator='\n'):
    """
        Function to get values from sparql string results. If there are more than one value
        we get them as list of strings (using the string separator), otherwise we get the single
        string value but still as a list.
        In addition:
          - if we have some same url and literal we take only the url.
    """
    if len(string) != 0:
        # Fixing Dbpedia's initial escape
        if string[0] == '\n':
            string = string[1:]

    values = string.split(separator)
    if len(values) == 1:
        # Cleaning literal's printing
        if string.startswith('* '):
            string = string[2:]
        return string
    else:
        # If we have same url and literal we take the first
        literals = []
        urls = []
        for v in values:
            if v.startswith('http://') or v.startswith('https://'):
                urls.append(v)
            else:
                # Cleaning literal's printing
                if v.startswith('* '):
                    v = v[2:]
                literals.append(v)

        if len(urls) != 0:
            literals_to_remove = []
            for u in urls:
                # We take only the name of resource removing after words like '(musician)'
                name = u.split('/')[-1].replace('_', ' ').split(' (')[0]
                for l in literals:
                    if name.lower() in l.lower():
                        literals_to_remove.append(l)
            cleaned_literals = list(set(literals) - set(literals_to_remove))
            urls.extend(cleaned_literals)
            return urls
        else:
            return literals


def format_sparql_query(query_filename, exact_match=False, language='en',
                        artist_name=None, album_name=None, track_name=None):
    query = get_query_from_file(query_filename)

    if language:
        query = query.replace("LANGUAGE", language)
    if artist_name:
        artist_name = format_sparql_string(artist_name)
        # Exact match not needed here! It's already done in all query files by default.
        query = query.replace("ARTIST_NAME", artist_name)
    if album_name:
        album_name = format_sparql_string(album_name)
        if exact_match:
            album_name = f"^{album_name}$"
        query = query.replace("ALBUM_NAME", album_name)
    if track_name:
        track_name = format_sparql_string(track_name)
        if exact_match:
            track_name = f"^{track_name}$"
        query = query.replace("TRACK_NAME", track_name)
    return query


def format_sparql_string(string):
    string = string.replace('(', '\\\\(')
    string = string.replace(')', '\\\\)')
    string = string.replace('?', '\\\\?')
    string = string.replace('$', '\\\\$')
    string = string.replace('^', '\\\\^')
    string = string.replace('*', '\\\\*')
    return string


def simplify_dbpedia_research(query):
    # Improving research on DBpedia
    # - For instance, by searching directly 'Another Brick In The Wall' instead of 'Another Brick in the Wall, Pt. 2
    query = simplify_research(query)
    # Removing 'NAME, Pt. n...' pattern
    query = re.sub(r'(, pt\. d*(.+))+', "", query)
    return query


def verify_result(query, result):
    query, result = query.lower(), result.lower()
    for word in re.findall(r'\w+', query):
        if word in re.findall(r'\w+', result):
            return True
    return False


def verify_dbpedia_url(url, name):
    """
    Function to verify DBpedia url and name correspondance

    :param url: DBpedia resource url.
    :param name: Name of the DBpedia resource.
    :return: True or false.
    """
    name_in_url = url.split("/")[-1].replace('_', ' ')
    return verify_result(name_in_url, name)
