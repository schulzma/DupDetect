#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 09:41:23 2019

@author: Martina Schulz

Beispiel zur Duplikaterkennung
Datenquelle: csv - Datei
Bibliothek: recordlinkage
"""
import os
import time

import recordlinkage as rl
import pandas as pd
# from recordlinkage.compare import Exact, String, Numeric, Date

start_time = time.time()

working_dir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(f'{working_dir}/../data')

file_ext = '.csv'
# input_file = 'bspSchiffe'
input_file = 'schiffe_DE_last30d'
output_file = f'{input_file}_recordlinkage_B_out'

df = pd.read_csv(os.path.join(data_dir, input_file + file_ext), index_col='MAROB_ID')

# Indexation step
print('indexing ...')
indexer = rl.Index()
indexer.block('MESSZEIT')
indexer.block('GEOGR_BREITE')
indexer.block('GEOGR_LAENGE')
indexer.block('KENNUNG')
pairs = indexer.index(df)

# Comparison step
print('... done.')
print('comparing ...')
comparer = rl.Compare()
comparer.exact('MESSZEIT', 'MESSZEIT', label='messzeit')
# comparer.exact('MESSZEIT_UNIX_TS', 'MESSZEIT_UNIX_TS', label='messzeit_unix_ts')
comparer.string('KENNUNG', 'KENNUNG', method='jarowinkler', threshold=0.85, label='kennung')
comparer.numeric('GEOGR_BREITE', 'GEOGR_BREITE', method=u'lin', offset=0.0, origin=0.0, scale=1.0, label='geogr_breite')
comparer.numeric('GEOGR_LAENGE', 'GEOGR_LAENGE', method=u'lin', offset=0.0, origin=0.0, scale=1.0, label='geogr_laenge')

compared = comparer.compute(pairs, df)
print('... done.')

# prozentualer Gesamtscore pro Datensatz
pcmax = compared.shape[1]  # col_count, 100%

compared.loc[:, 'Score'] = 1 - (abs(compared.sum(axis=1) - pcmax) / pcmax)

# Classification step
matches = compared[(compared.messzeit == 1) | (compared.Score > .98)]
# matches = compared[compared.Score > .98]
print(f'Anzahl Matches: {len(matches)}')

non_matches = compared[(compared.messzeit == 0) | (compared.Score < .98)]
print(f'Anzahl Non-Matches: {len(non_matches)}')

# send output to csv
# compared.to_csv(os.path.join(working_dir, output_file + file_ext))
matches.to_csv(os.path.join(working_dir, f'{output_file}_matches' + file_ext))
# non_matches.to_csv(os.path.join(working_dir, f'{output_file}_non_matches' + file_ext))
print(f'ran in {time.time() - start_time} seconds')
