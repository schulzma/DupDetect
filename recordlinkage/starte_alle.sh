#!/bin/bash
for i in $(cat ../data/nums)
do python csv_example_recordlinkage_SN.py ../data/exp_$i.csv > output_$i.log
done
