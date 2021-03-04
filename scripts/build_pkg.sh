#!/bin/bash

export TWINE_REPOSITORY='testpypi'
export TWINE_USERNAME='user'
export TWINE_PASSWORD='password'

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

cd "$REPO" || exit

echo "Building package..."
python3 "$REPO/setup.py" bdist_wheel

echo "Checking package..."
twine check --strict dist/*

echo "Uploading package..."
twine upload --verbose dist/*

echo "Removing package directories..."
rm -rf "$REPO/dist" || exit
rm -rf "$REPO/build" || exit
rm -rf "$REPO/src/$PROJECT.egg-info" || exit
