#!/bin/bash
for i in $(cat ../data/nums)
do python csv_example_pandas_dedupe.py ../data/exp_$i.csv > output_$i.log
done
