#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 13:30:46 2019

@author: Martina Schulz

Beispiel zur Duplikaterkennung
Datenquelle: csv - Datei
Bibliothek: pandas_dedupe

Usage:
    csv_example_pandas_dedupe.py <filename>

Arguments:
    <filename>  Name der Eingabedatei

Options:
    -h --help   Zeigt diese Hilfe.

"""
import os
from pathlib import Path
import time
from functools import wraps
from docopt import docopt

import pandas as pd
import pandas_dedupe


def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        start_time = time.time()
        result = function(*args, **kwargs)
        print(f"Total time running {function.__name__}: {time.time() - start_time} seconds")
        return result

    return function_timer


def read_file(f):
    """
    Eingabedatei in ein Pandas-DataFrame einlesen
    :param f: Eingabedatei
    :return: DataFrame
    """
    try:
        # load dataframe
        df = pd.read_csv(f, index_col='MAROB_ID')
        df['LAT_LON'] = df.apply(lambda row: [row['GEOGR_BREITE'], row['GEOGR_LAENGE']], axis=1)
        return df
    except FileNotFoundError:
        print(f"{f} nicht gefunden!")


@fn_timer
def start_p_dedupe(df):
    """
    Doppelte Daten im Dataframe erkennen und Gesamt-Score pro Datensatz berechnen
    :param df: DataFrame mit Eingangsdaten
    :return: DataFrame mit dem Ergebnis
    """
    # initiate deduplication
    fields = [('MESSZEIT', 'Exact'), ('KENNUNG', 'Exact'),
              # ('GEOGR_BREITE', 'String'), ('GEOGR_LAENGE', 'String'),
              ('LAT_LON', 'LatLong'),
              ('HORIZONTALE_SICHT', 'ShortString', 'has missing'),
              ('WETTER', 'ShortString', 'has missing')]
    df_final = pandas_dedupe.dedupe_dataframe(df, fields)
    return df_final


def write_data(d):
    # send output to csv
    d.to_csv(output_file)


if __name__ == '__main__':
    # args
    args = docopt(__doc__)
    input_file = args["<filename>"]

    output_file = f'pandas_dedupe_out_{Path(input_file).name}'

    working_dir = os.path.abspath(os.path.dirname(__file__))
    settings_file = os.path.join(working_dir, 'dedupe_dataframe_learned_settings')
    training_file = os.path.join(working_dir, 'dedupe_dataframe_training.json')

    dat = start_p_dedupe(read_file(input_file))
    write_data(dat)
