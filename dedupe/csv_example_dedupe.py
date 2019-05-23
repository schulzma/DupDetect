#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 13:16:40 2019

https://github.com/dedupeio/dedupe-examples.git

@author: Martina Schulz

Beispiel zur Duplikaterkennung
Datenquelle: csv - Datei
Bibliothek: dedupe

Usage:
    csv_example_dedupe.py <filename>

Arguments:
    <filename>  Name der Eingabedatei

Options:
    -h --help   Zeigt diese Hilfe.

"""
import os
import csv
import re
import time
import dedupe
from unidecode import unidecode
from pathlib import Path
from functools import wraps
from docopt import docopt


def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        start_time = time.time()
        result = function(*args, **kwargs)
        print(f"Total time running {function.__name__}: {time.time() - start_time} seconds")
        return result

    return function_timer


def sim_num_perc(field_1, field_2, pcmax=98):
    """
    Relative numerische Aehnlichkeit
    :param field_1: Parameter 1
    :param field_2: Parameter 2
    :param pcmax: prozentualer Toleranzschwellwert, default: 98 %
    :return: Aehnlichkeit (zwischen 0 fuer keine und 1 fuer komplette Identitaet)
    """
    try:
        f1 = float(field_1)
        f2 = float(field_2)
        pc = abs(f1 - f2) / max(abs(f1), abs(f2)) * 100
#        print(1.0 - (pc / pcmax)) if pc < pcmax else print(0.0)
        return 1.0 - (pc / pcmax) if pc < pcmax else 0.0
    except ValueError:
        pass


def sim_num_abs(field_1, field_2, dmax=.1):
    """
    Numerische Aehnlichkeit mit absoluter Differenz als Toleranz
    :param field_1: Parameter 1
    :param field_2: Parameter 2
    :param dmax: maximale absolute Differenz, default: 0.1
    :return: Aehnlichkeit (zwischen 0 fuer keine und 1 fuer komplette Identitaet)
    """
    try:
        f1 = float(field_1)
        f2 = float(field_2)
        d = abs(f1 - f2)
        # print(f'f1:{f1} f2:{f2} d:{d}')
        if d <= dmax:
            sim = 1.0 - (d / dmax)
            # print(sim)
            return sim
        else:
            # print(0.0)
            return 0.0
    except ValueError:
        pass


def num_abs_ident(field_1, field_2):
    try:
        return sim_num_abs(field_1, field_2, 0)
    except:
        pass


def sim_ww(field_1, field_2):
    try:
#        print(field_1, field_2)
        if ((field_1 is None) and (field_2 in ['509', '510'])) or ((field_2 is None) and (field_1 in ['509', '510'])):
#            print(1)
            return 1
        else:
            return sim_num_perc(field_1, field_2)
    except:
        pass


def pre_process(column):
    """
    Do a little bit of data cleaning with the help of Unidecode and Regex.
    Things like casing, extra spaces, quotes and new lines can be ignored.
    """
    try:  # python 2/3 string differences
        if isinstance(column, list):
            column = [str(x) for x in column]
            column = [x.encode('utf8') for x in column]
        else:
            column = column.decode('utf8')
    except AttributeError:
        pass
    if not isinstance(column, list):
#        column = [unidecode(x) for x in column]
#        column = [re.sub('  +', ' ', x) for x in column]
#        column = [re.sub('\n', ' ', x) for x in column]
#        column = [x.strip().strip('"').strip("'").lower().strip() for x in column]
#    else:
        column = unidecode(column)
        column = re.sub('  +', ' ', column)
        column = re.sub('\n', ' ', column)
        column = column.strip().strip('"').strip("'").lower().strip()
    # If data is missing, indicate that by setting the value to `None`
    if not column:
        column = None
    return column


def read_data(filename):
    """
    Read in our data from a CSV file and create a dictionary of records, 
    where the key is a unique record ID and each value is dict
    """
    print('importing data ...')
    data_d = {}
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = [(k, pre_process(v)) for (k, v) in row.items()]
            row_id = int(row['MAROB_ID'])
            data_d[row_id] = dict(clean_row)
    #            data_d[row_id]['LAT_LON']=(float(data_d[row_id]['LAT']),float(data_d[row_id]['LON']))

    return data_d


@fn_timer
def start_dedupe(df):
    # If a settings file already exists, we'll just load that and skip training
    if os.path.exists(settings_file):
        print('reading from', settings_file)
        with open(settings_file, 'rb') as f:
            deduper = dedupe.StaticDedupe(f)

    else:
        # ## Training

        # Define the fields dedupe will pay attention to
        fields = [
            {'field': 'MESSZEIT', 'type': 'Exact'},
            {'field': 'KENNUNG', 'type': 'Exact'},
            {'field': 'GEOGR_BREITE', 'type': 'Custom', 'comparator': sim_num_abs},
            {'field': 'GEOGR_LAENGE', 'type': 'Custom', 'comparator': sim_num_abs},
            {'field': 'HORIZONTALE_SICHT', 'type': 'ShortString', 'has missing': True},
            {'field': 'WETTER', 'type': 'Custom', 'comparator': sim_ww, 'has missing': True},
        ]

        # Create a new deduper object and pass our data model to it.
        deduper = dedupe.Dedupe(fields)

        # To train dedupe, we feed it a sample of records.
        deduper.sample(df, 15000, .5)

        # If we have training data saved from a previous run of dedupe,
        # look for it and load it in.
        # __Note:__ if you want to train from scratch, delete the training_file
        if os.path.exists(training_file):
            print('reading labeled examples from ', training_file)
            with open(training_file, 'rb') as f:
                deduper.readTraining(f)

        # ## Active learning
        # Dedupe will find the next pair of records
        # it is least certain about and ask you to label them as duplicates
        # or not.
        # use 'y', 'n' and 'u' keys to flag duplicates
        # press 'f' when you are finished
        print('starting active labeling...')

        dedupe.consoleLabel(deduper)

        # Using the examples we just labeled, train the deduper and learn
        # blocking predicates
        deduper.train()

        # When finished, save our training to disk
        with open(training_file, 'w') as tf:
            deduper.writeTraining(tf)

        # Save our weights and predicates to disk.  If the settings file
        # exists, we will skip all the training and learning next time we run
        # this file.
        with open(settings_file, 'wb') as sf:
            deduper.writeSettings(sf)

    threshold = deduper.threshold(df, recall_weight=1)
    print(f'threshold: {threshold}')

    print('clustering...')
    # clustered_dupes = deduper.match(df, .98)
    clustered_dupes = deduper.match(df, threshold)

    print(f'# duplicate sets {len(clustered_dupes)}')
    return clustered_dupes


def write_data(d):
    # ## Writing Results

    # Write our original data back out to a CSV with a new column called
    # 'Cluster ID' which indicates which records refer to each other.

    cluster_membership = {}
    cluster_id = 0
    for (cluster_id, cluster) in enumerate(d):
        id_set, scores = cluster
        for record_id, score in zip(id_set, scores):
            cluster_membership[record_id] = {
                "cluster id": cluster_id,
                "confidence": score
            }

    singleton_id = cluster_id + 1

    with open(output_file, 'w') as f_output, open(input_file) as f_input:
        writer = csv.writer(f_output)
        reader = csv.reader(f_input)

        heading_row = next(reader)
        heading_row.insert(0, 'confidence_score')
        heading_row.insert(0, 'Cluster ID')

        writer.writerow(heading_row)

        for row in reader:
            row_id = int(row[0])
            if row_id in cluster_membership:
                cluster_id = cluster_membership[row_id]["cluster id"]
                row.insert(0, cluster_membership[row_id]['confidence'])
                row.insert(0, cluster_id)
            else:
                row.insert(0, None)
                row.insert(0, singleton_id)
                singleton_id += 1
            writer.writerow(row)


if __name__ == '__main__':
    # args
    args = docopt(__doc__)
    input_file = args["<filename>"]

    output_file = f'dedupe_out_{Path(input_file).name}'

    working_dir = os.path.abspath(os.path.dirname(__file__))
    settings_file = os.path.join(working_dir, 'dedupe_dataframe_learned_settings')
    training_file = os.path.join(working_dir, 'dedupe_dataframe_training.json')

    dat = start_dedupe(read_data(input_file))
    write_data(dat)
