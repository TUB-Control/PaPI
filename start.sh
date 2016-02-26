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

#Set fonts for Help.
NORM=`tput sgr0`
BOLD=`tput bold`
REV=`tput smso`

#Help function
function HELP_FUNC {
  echo -e \\n"Help documentation for ${BOLD}${SCRIPT}PaPI${NORM}"\\n
  echo -e "${REV}Basic usage:${NORM} ${BOLD}$SCRIPT start.sh ${NORM}"\\n
  echo "Command line switches are optional."
  echo "${REV}-f${NORM}  --Starts PaPI in full screen mode."
  echo "${REV}-r${NORM}  --Starts PaPI with activated run mode."
  echo "${REV}-v${NORM}  --Displays the version of PaPI"
  echo -e "${REV}-h${NORM}  --Displays this help message."\\n
  echo "Command line arguments are optional."
  echo "${REV}-c${NORM}  --Start PaPI with the given configuration(PaPI loads arg-cfg after start)"
  echo -e "${REV}-u${NORM}  --Specify another user config."\\n
  echo -e "Example: ${BOLD}$SCRIPT -f -r -c ./cfg.xml${NORM}"\\n
  echo -e "More documentation can be found here: Documentation can be found here: http://tub-control.github.io/PaPI/dev/"\\n


  exit 1
}


OPT_U="-u ~/.papi/config.xml"
OPT_R=""
OPT_F=""
OPT_C=""
OPT_V=""

### Start getopts code ###
### some examples: http://tuxtweaks.com/2014/05/bash-getopts/
while getopts :c:frvu:h FLAG; do
  case $FLAG in
    c)  #set option "c"
     OPT_C="-c $OPTARG"
      ;;
    f)  #set option "f"
      OPT_F="-f"
      ;;
    r)  #set option "r"
      OPT_R="-r"
      ;;
    u)  #set option "u"
      OPT_U="-u $OPTARG"
      ;;
    v)  #set option "v"
      OPT_V="-v"
      ;;
    h)  #show help
      HELP_FUNC
      ;;
    \?) #unrecognized option - show help
      echo -e \\n"Option -${BOLD}$OPTARG${NORM} not allowed."
      echo "test"
      ;;
  esac
done

shift $((OPTIND-1))  #This tells getopts to move on to the next argument.

### End getopts code ###



$PYTHON $DIR/main.py $OPT_C $OPT_R $OPT_F $OPT_U $OPT_V
