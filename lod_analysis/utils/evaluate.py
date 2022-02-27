import ast
import os
import pandas as pd

from utils.excel import EXCELS_DIRECTORY, save_excel


def evaluate_data(verbose=True):
    dataframes = {}
    for filename in os.listdir(EXCELS_DIRECTORY):
        f = os.path.join(EXCELS_DIRECTORY, filename)
        # checking if it is an Excel file and not an evaluation file
        if os.path.isfile(f) and '.xlsx' in filename and 'evaluation' not in filename:
            dataframes[filename] = pd.read_excel(f, index_col=[0])

    for filename, dataframe in dataframes.items():
        target = None
        full = False
        if filename.startswith('artists'):
            target = 'artist'
        if filename.startswith('albums'):
            target = 'album'
        if filename.startswith('tracks'):
            target = 'track'
        if 'full' in filename:
            full = True
        if target is None:
            continue
        if verbose:
            print(f"-----------  EVALUATING {target.upper()}S FROM {filename} ({dataframe.shape[0]} elements)  ----------- ")
        data = dataframe.to_dict()
        data['genius_completeness'] = {}
        data['dbpedia_completeness'] = {}
        data['geonames_completeness'] = {}
        for source in ['genius', 'dbpedia', 'geonames']:
            for i, entry in data[source].items():
                if isinstance(entry, str):
                    entry = ast.literal_eval(entry)
                else:
                    entry = None
                if source == 'genius':
                    data['genius_completeness'].update({i: evaluate_completeness_genius(entry, target)})
                if source == 'dbpedia':
                    data['dbpedia_completeness'].update({i: evaluate_completeness_dbpedia(entry, target, full)})
                if source == 'geonames':
                    data['geonames_completeness'].update({i: evaluate_completeness_geonames(entry)})
        if verbose:
            print(f"----------- {target.upper()}S EVALUATION COMPLETED SUCCESSFULLY! -----------")

        # Saving evaluation
        save_excel(data, target+'s', get_full_info=full, evaluate=True, verbose=verbose)


def evaluate_completeness_genius(data, target):
    if not data:
        return 0
    # At least every target has url and annotations.description!
    num_fields = 2
    num_empty = 0

    description = data['annotations']['description']
    if description == '<p>?</p>':
        num_empty += 1

    if target == 'artist':
        num_fields += 1
        alternate_names = data['annotations']['alternate_names']
        if alternate_names is None:
            num_empty += 1
        else:
            if len(alternate_names) == 0:
                num_empty += 1

    if target == 'album' or target == 'track':
        num_fields += 3
        producers = data['annotations']['producers']
        if producers is None:
            num_empty += 1
        else:
            if len(producers) == 0:
                num_empty += 1
        writers = data['annotations']['writers']
        if writers is None:
            num_empty += 1
        else:
            if len(writers) == 0:
                num_empty += 1
        labels = data['annotations']['labels']
        if labels is None:
            num_empty += 1
        else:
            if len(labels) == 0:
                num_empty += 1

    if target == 'track':
        num_fields += 1
        lyrics = data['lyrics']
        if lyrics is None:
            num_empty += 1

    return (num_fields - num_empty) / num_fields


def evaluate_completeness_dbpedia(data, target, full=False):
    if not data:
        return 0
    num_fields = 0
    num_empty = 0

    if target == 'artist':
        # ?artist ?artist_name ?wiki ?hometown ?birth_date ?death_date ?start_year ?end_year ?abstract
        fields = ['artist', 'artist_name', 'wiki', 'hometown', 'birth_date', 'death_date',
                  'start_year', 'end_year', 'abstract']
        num_fields += len(fields)
        for k in fields:
            if data.get(k, None) is None:
                num_empty += 1
        if full:
            # ?aliases ?labels ?plays_in ?genres ?actual_members ?old_members ?related_artists
            other_fields = ['aliases', 'labels', 'plays_in', 'genres', 'actual_members',
                            'old_members', 'related_artists']
            num_fields += len(other_fields)
            for k in other_fields:
                if data.get(k, None) is None:
                    num_empty += 1

    if target == 'album':
        # ?album ?album_name ?artist ?artist_name ?wiki ?hometown ?abstract
        fields = ['album', 'album_name', 'artist', 'artist_name', 'wiki', 'hometown',
                  'abstract']
        num_fields += len(fields)
        for k in fields:
            if data.get(k, None) is None:
                num_empty += 1

    if target == 'track':
        # ?track ?track_name ?artist ?artist_name ?wiki ?hometown ?abstract
        fields = ['track', 'track_name', 'artist', 'artist_name', 'wiki', 'hometown',
                  'abstract']
        num_fields += len(fields)
        for k in fields:
            if data.get(k, None) is None:
                num_empty += 1

    if (target == 'track' or target == 'album') and full:
        # ?released ?producers ?writers ?awards ?labels ?genres ?related_artists
        other_fields = ['released', 'producers', 'writers', 'awards', 'labels', 'genres',
                        'related_artists']
        num_fields += len(other_fields)
        for k in other_fields:
            if data.get(k, None) is None:
                num_empty += 1

    return (num_fields - num_empty) / num_fields


def evaluate_completeness_geonames(data):
    if not data:
        return 0

    # ?place ?place_name ?country_code ?postal_code ?lat ?long ?wiki ?geo_link ?population
    fields = ['place', 'place_name', 'country_code', 'postal_code', 'lat', 'long',
              'wiki', 'geo_link', 'population']
    num_fields = len(fields)
    num_empty = 0
    for k in fields:
        if data.get(k, None) is None:
            num_empty += 1

    return (num_fields - num_empty) / num_fields
