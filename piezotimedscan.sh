#!/bin/bash
x=${1}
p=$(pwd)
res1=$(date +%s)

while [ $((res2-res1)) -lt $((x * 60 * 60)) ] 
	do
	res2=$(date +%s)
	echo $((res2-res1))
	python ${p}/piezoscandatasnoplot.py 0.1
done
