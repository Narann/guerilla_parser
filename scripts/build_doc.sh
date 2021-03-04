#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

REPO=$(realpath "$DIR"/..)

export PYTHONPATH=$REPO/src

PROJECT=guerilla_parser

PYENV=$REPO/$PROJECT-pyenv3

echo "Checking python virtual env is available..."
if [ ! -d "$PYENV" ]; then
    echo "$PYENV does not exist. Quitting..."
    exit
fi

echo "Sourcing python env $PYENV"
source "$PYENV/bin/activate"

cd "$REPO/doc" || exit

echo "Testing documentation examples..."
#sphinx-build -b doctest . _build/html || exit

echo "Building documentation..."
sphinx-build -T -E -a -b html -D language=en . _build/html
