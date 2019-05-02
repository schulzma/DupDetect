#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 13:30:46 2019

@author: Martina Schulz

Beispiel zur Duplikaterkennung
Datenquelle: csv - Datei
Bibliothek: pandas_dedupe
"""

import os
import time

import pandas as pd
import pandas_dedupe

start_time = time.time()

working_dir = os.path.abspath(os.path.dirname(__file__))
print(f'Working-Dir: {working_dir}')
data_dir = os.path.normpath(f'{working_dir}/../data')
print(f'Data-Dir: {data_dir}')

working_dir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(f'{working_dir}/../data')

file_ext = '.csv'
input_file = 'schiffe_DE_last30d'
# input_file = 'bspSchiffe'
output_file = f'{input_file}_pandas_dedupe_out'

settings_file = os.path.join(working_dir, 'dedupe_dataframe_learned_settings')
training_file = os.path.join(working_dir, 'dedupe_dataframe_training.json')

# load dataframe
df = pd.read_csv(os.path.join(data_dir, input_file + file_ext), index_col='MAROB_ID')

# initiate deduplication
# df_final = pandas_dedupe.dedupe_dataframe(df, ['MESSZEIT', ('KENNUNG', 'Text'), 'LAT', 'LON'], canonicalize=True)
df_final = pandas_dedupe.dedupe_dataframe(df, ['MESSZEIT', ('KENNUNG', 'Text'), 'GEOGR_BREITE', 'GEOGR_LAENGE'])

# send output to csv
df_final.to_csv(output_file + file_ext)
print(f'ran in {time.time() - start_time} seconds')
