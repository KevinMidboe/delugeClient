#!/usr/bin/bash

PYPI_VERSION=$(pip3 show delugeClient-kevin | awk '$1 ~ /Version:/ { print $2 }')
SOURCE_VERSION=$(python3 delugeClient/__version__.py)

echo "hello"
echo "pypi version: $PYPI_VERSION"
echo "source version: $SOURCE_VERSION"

function version {
  echo "$@" | awk -F. '{ printf("%d%03d%03d%03d\n", $1,$2,$3,$4); }';
}

if [ $(version $SOURCE_VERSION) -gt $(version $PYPI_VERSION) ]; then
  echo "source is newer than pypi"
  exit 0
else
  exit 1
  echo "source is same or oldre, but not newer"
fi