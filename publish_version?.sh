#!/usr/bin/bash

PYPI_VERSION=$(pip3 show delugeClient-kevin | awk '$1 ~ /Version:/ { print $2 }')
SOURCE_VERSION=$(python3 delugeClient/__version__.py)

printf "Source version:\t\t %s\n" $SOURCE_VERSION
printf "Remote PyPi version:\t %s\n" $PYPI_VERSION

function version {
  echo "$@" | awk -F. '{ printf("%d%03d%03d%03d\n", $1,$2,$3,$4); }';
}

if [ $(version $SOURCE_VERSION) -gt $(version $PYPI_VERSION) ]; then
  echo "Soure is newer than remote, publishing!"
  exit 0
else
  echo "Source is same or oldre than remote, nothing to do."
  exit 1
fi