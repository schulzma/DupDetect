#!/bin/bash
for i in $(cat ../data/nums)
do 
grep ^Tot output_$i.log|awk '{print $5}'|sed 's/\./,/g'
done;
