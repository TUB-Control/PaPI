#!/bin/bash


# http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in/246128#246128
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"


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

$PYTHON $DIR/main.py $ARGS
