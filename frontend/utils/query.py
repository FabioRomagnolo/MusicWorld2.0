import re


def simplify_research(query):
    query = query.lower()
    # Removing phrases inside brackets []
    query = re.sub(r"\[(.*)\]", "", query)

    # Removing patterns in ' - ...' or ' ...(end of string)' or '(...)
    regex_patterns = [
        r'(feat\.|featuring|with)', r'(remastered|remaster)',
        r'(remixed|remix)', r'cover', r'from', r'instrumental',
        r'demo', r'version', 'radio', r'(edition|edit)',
        r'deluxe', r'expanded', r'ep', r'[0-9]*th anniversary',
        r'live', r'acoustic'
    ]
    for r in regex_patterns:
        query = re.sub(r'\((.*){0}(.*)\)'.format(r), "", query)
        query = re.sub(r' -(.*){0}(.*)'.format(r), "", query)
        query = re.sub(r'( {0}(.*))$'.format(r), "", query)

    # Removing particular words and chars
    to_replace = ['"', ]
    for word in to_replace:
        query = query.replace(word, '')

    # Removing empty brackets
    query = re.sub(r'\((\s*)(-*?)\)', "", query)

    # Removing specific final patterns
    final_regex_patterns = [
        '-', ':', ';'
    ]
    for f in final_regex_patterns:
        query = re.sub(r'({0}+(\s*))$'.format(f), "", query)

    # Removing final spaces
    query = "".join(query.rstrip())
    return query


def verify_result(query, result):
    query, result = query.lower(), result.lower()
    for word in re.findall(r'\w+', query):
        if word in re.findall(r'\w+', result):
            return True
    return False
