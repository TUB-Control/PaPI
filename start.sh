#!/bin/bash

PYTHON=python3.4

if [ ! -z "$1" ]
    then
        $PYTHON main.py -c $1
    else
        $PYTHON main.py
fi

