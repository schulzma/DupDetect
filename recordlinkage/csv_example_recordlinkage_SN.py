#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 11:58:50 2019

@author: Martina Schulz

Beispiel zur Duplikaterkennung
Datenquelle: csv - Datei
Bibliothek: recordlinkage

Usage:
    csv_example_recordlinkage_SN.py <filename>

Arguments:
    <filename>  Name der Eingabedatei

Options:
    -h --help   Zeigt diese Hilfe.

"""
import time
import recordlinkage as rl
from functools import wraps
from pathlib import Path
from docopt import docopt
from recordlinkage.base import BaseCompareFeature
import pandas as pd

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


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
        df = pd.read_csv(f, index_col='MAROB_ID')
        return df
    except FileNotFoundError:
        print(f"{f} nicht gefunden!")


class CompareWetter(BaseCompareFeature):

    def _compute_vectorized(self, s1, s2):
        """
        Wetter vergleichen, wenn 509 oder 510 dann auch 1.0 zurückgeben
        """
        sim = (s1 == s2) | (s1 == 509.0) | (s2 == 509.0) | (s1 == 510.0) | (s2 == 510.0) | s1.empty | s2.empty
        return sim.astype(float)


@fn_timer
def start_rl(df):
    """
    Doppelte Daten im Dataframe erkennen und Gesamt-Score pro Datensatz berechnen
    :param df: DataFrame mit Eingangsdaten
    :return: zwei DataFrames mit dem Ergebnis aller durchgefuehrten Vergleiche und den Treffern mit einem Score >= .99
    """

    # Indexation step
    indexer = rl.index.SortedNeighbourhood(
        'MESSZEIT', window=3, block_on=['KENNUNG']
    )
    pairs = indexer.index(df)

    # Comparison step
    comparer = rl.Compare()
    comparer.exact('MESSZEIT', 'MESSZEIT', label='messzeit')
    comparer.exact('KENNUNG', 'KENNUNG', label='kennung')
    comparer.numeric('GEOGR_BREITE', 'GEOGR_BREITE', method=u'lin', offset=0.0, label='geogr_breite')
    comparer.numeric('GEOGR_LAENGE', 'GEOGR_LAENGE', method=u'lin', offset=0.0, label='geogr_laenge')
    comparer.numeric('HORIZONTALE_SICHT', 'HORIZONTALE_SICHT', method=u'lin', offset=10.0, missing_value=1,
                     label='horizontale_sicht')
    comparer.add(CompareWetter('WETTER', 'WETTER', label='wetter2'))

    compared = comparer.compute(pairs, df)

    # prozentualer Gesamtscore pro Datensatz
    pcmax = compared.shape[1]  # col_count, 100%
    compared.loc[:, 'Score'] = 1 - (abs(compared.sum(axis=1) - pcmax) / pcmax)

    # Classification step
    matches = compared[(compared.messzeit == 1) & (compared.kennung == 1) & (compared.Score >= .99)]

    return compared, matches


def write_data(c, m):
    # send output to csv
    c.to_csv(output_file)
    m.to_csv(f'{output_file}_matches')


if __name__ == '__main__':
    # args
    args = docopt(__doc__)
    input_file = args["<filename>"]

    # start_time = time.time()

    output_file = f'recordlinkage_SN_out_{Path(input_file).name}'
    cmp, match = start_rl(read_file(input_file))
    print(f'Anzahl Matches: {len(match)}')

    write_data(cmp, match)

    # print(f'ran in {time.time() - start_time} seconds')
