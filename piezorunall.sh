#!/bin/bash
x=${1}
p=$(pwd)
for (( i=0 ; i <= x ; i++ ))
	do
	python ${p}/piezoscandatas.py -P 0.1
done
