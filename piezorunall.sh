#!/bin/bash
x=${1}
p=$(pwd)
for (( i=0 ; i <= x ; i++ ))
	do
	python ${p}/piezoscandatasnoplot.py 0.1
done