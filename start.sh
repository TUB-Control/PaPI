#!/bin/bash

PYTHON=python3.4

mkdir -p ~/.papi/


UCFG=~/.papi/config.xml

ARGS=

if [ ! -z "$1" ]
then
   ARGS="$ARGS -c $1"
fi

if [ ! -z "$UCFG" ] 
then
   ARGS="$ARGS -u $UCFG"
fi

$PYTHON main.py $ARGS
