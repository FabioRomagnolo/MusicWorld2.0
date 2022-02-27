import re


def simplify_research(query):
    query = query.lower()
    # Removing phrases inside brackets [] -> Applying at least 2 times
    query = re.sub(r"\[(.*?)\]", "", query)
    query = re.sub(r"\[(.*?)\]", "", query)
    # Removing featuring patterns
    query = re.sub(r'\(?(feat\.|featuring|with) (.*)\)?', "", query)
    # Removing 'Remastered - year' pattern
    query = re.sub(r'\(?(remastered|remaster)( -)*? [0-9]*\)?', "", query)
    query = re.sub(r'\(?[0-9]*( -)*? (remastered|remaster)\)?', "", query)
    # Removing 'Remix - year' pattern
    query = re.sub(r'\(?(remixed|remix)( -)*? [0-9]*\)?', "", query)
    query = re.sub(r'\(?[0-9]*( -)*? (remixed|remix)\)?', "", query)
    # Removing 'ARTIST Cover pattern'
    query = re.sub(r'-(.*?)cover', "", query)
    # Removing 'From the "FILM" soundtrack' and similar patterns
    query = re.sub(r' - from (.*)', "", query)
    query = re.sub(r'\((.*?)from(.*)\)', "", query)
    # Removing 'Instrumental' and similar patterns
    query = re.sub(r' -(.*?)instrumental(.*?)', "", query)
    query = re.sub(r'\((.*?)instrumental(.*?)\)', "", query)
    # Removing 'Demo' and similar patterns
    query = re.sub(r' -(.*?)demo(.*?)', "", query)
    query = re.sub(r'\((.*?)demo(.*?)\)', "", query)
    # Removing "X version" pattern
    query = re.sub(r'\((.*) version\)', "", query)
    # Removing '(X edition)' pattern
    query = re.sub(r'\((.*) edition\)', "", query)
    # Removing '(... deluxe ...)' pattern
    query = re.sub(r'\((.*?)deluxe(.*?)\)', "", query)
    # Removing "Xth anniversary" pattern
    query = re.sub(r'[0-9]*th anniversary(.*)', "", query)
    # Removing '(Live ...)' pattern
    query = re.sub(r'\((.*?)live(.*?)\)', "", query)
    query = re.sub(r'-(.*?)live(.*?)', "", query)
    # Removing useless words and chars
    to_replace = ['"', ]
    for word in to_replace:
        query = query.replace(word, '')
    # Removing empty brackets
    query = re.sub(r'\((\s*)(-*?)\)', "", query)
    query = re.sub(r'\[(\s*)(-*?)\]', "", query)
    # Removing ' - ...' at the end of string
    query = re.sub(r'(\s*-+(.*?))$', "", query)
    # Removing ': ' at the end of string
    query = re.sub(r'(:+(\s?))$', "", query)
    # Removing final spaces
    query = "".join(query.rstrip())
    return query


def verify_result(query, result):
    query, result = query.lower(), result.lower()
    for word in re.findall(r'\w+', query):
        if word in re.findall(r'\w+', result):
            return True
    return False
