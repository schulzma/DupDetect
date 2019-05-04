#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 13:16:40 2019

https://github.com/dedupeio/dedupe-examples.git

@author: Martina Schulz

Beispiel zur Duplikaterkennung
Datenquelle: csv - Datei
Bibliothek: dedupe
"""
import os
import csv
import re
import time
import dedupe
from unidecode import unidecode


start_time = time.time()


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
        return 1.0 - (pc / pcmax) if pc < pcmax else 0.0
    except ValueError:
        pass


def sim_num_abs(field_1, field_2, dmax=.11):
    """
    Numerische Aehnlichkeit mit absoluter Differenz als Toleranz
    :param field_1: Parameter 1
    :param field_2: Parameter 2
    :param dmax: maximale absolute Differenz, default: 0.11
    :return: Aehnlichkeit (zwischen 0 fuer keine und 1 fuer komplette Identitaet)
    """
    try:
        f1 = float(field_1)
        f2 = float(field_2)
        d = abs(f1 - f2)
        return 1.0 - (d / dmax) if d < dmax else 0.0
    except ValueError:
        pass


def num_abs_ident(field_1, field_2):
    try:
        return sim_num_abs(field_1, field_2, 0)
    except:
        pass


def pre_process(column):
    """
    Do a little bit of data cleaning with the help of Unidecode and Regex.
    Things like casing, extra spaces, quotes and new lines can be ignored.
    """
    try:  # python 2/3 string differences
        column = column.decode('utf8')
    except AttributeError:
        pass
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

    data_d = {}
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = [(k, pre_process(v)) for (k, v) in row.items()]
            row_id = int(row['MAROB_ID'])
            data_d[row_id] = dict(clean_row)
    #            data_d[row_id]['LAT_LON']=(float(data_d[row_id]['LAT']),float(data_d[row_id]['LON']))
    return data_d


working_dir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(f'{working_dir}/../data')

file_ext = '.csv'
input_file = 'schiffe_DE_last30d'
# input_file = 'schiffe_DE_70000'
# input_file = 'bspSchiffe'
output_file = f'{input_file}_dedupe_out{file_ext}'

settings_file = os.path.join(working_dir, 'dedupe_dataframe_learned_settings')
training_file = os.path.join(working_dir, 'dedupe_dataframe_training.json')

print('importing data ...')
data_d = read_data(os.path.join(data_dir, input_file + file_ext))

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
        # {'field': 'MESSZEIT_UNIX_TS', 'type': 'Custom', 'comparator': num_abs_ident },
        #        {'field' : 'MESSZEIT', 'type': 'String'},
        #        {'field' : 'MESSZEIT','type': 'DateTime',
        #         'fuzzy': False, 'dayfirst': False, 'yearfirst': True},
        {'field': 'KENNUNG', 'type': 'String'},
        {'field': 'GEOGR_BREITE', 'type': 'Custom', 'comparator': sim_num_abs},
        {'field': 'GEOGR_LAENGE', 'type': 'Custom', 'comparator': sim_num_abs},
        # {'field': 'LAT', 'type': 'Custom', 'comparator': sim_num_abs},
        # {'field': 'LON', 'type': 'Custom', 'comparator': sim_num_abs},
        # {'field' : 'LAT_LON', 'type': 'LatLong'},
    ]

    # Create a new deduper object and pass our data model to it.
    deduper = dedupe.Dedupe(fields)

    # To train dedupe, we feed it a sample of records.
    deduper.sample(data_d, 15000, .8)

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

threshold = deduper.threshold(data_d, recall_weight=2.5)
print(f'threshold: {threshold}')

print('clustering...')
clustered_dupes = deduper.match(data_d, .98)
# clustered_dupes = deduper.match(data_d, threshold)

print(f'# duplicate sets {len(clustered_dupes)}')

# ## Writing Results

# Write our original data back out to a CSV with a new column called 
# 'Cluster ID' which indicates which records refer to each other.

cluster_membership = {}
cluster_id = 0
for (cluster_id, cluster) in enumerate(clustered_dupes):
    id_set, scores = cluster
    for record_id, score in zip(id_set, scores):
        cluster_membership[record_id] = {
            "cluster id": cluster_id,
            "confidence": score
        }

singleton_id = cluster_id + 1

with open(os.path.join(working_dir, output_file), 'w') as f_output, open(
        os.path.join(data_dir, input_file + file_ext)) as f_input:
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
print(f'ran in {time.time() - start_time} seconds')
