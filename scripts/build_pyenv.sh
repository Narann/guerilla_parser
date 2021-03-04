#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

REPO=$(realpath "$DIR"/..)

PROJECT=guerilla_parser

build_pyenv()
{
PY_VERSION=$1

PYENV=$REPO/$PROJECT-pyenv$PY_VERSION

echo "PYENV dir '$PYENV'"

echo "Checking python virtual env is available..."
if [ ! -d "$PYENV" ]; then
    echo "$PYENV does not exist, creating it..."
    virtualenv -p "python$PY_VERSION" "$PYENV"
fi

echo "Sourcing python env $PYENV"
source "$PYENV/bin/activate"

echo "Updating pip..."
pip install pip --upgrade

echo "Installing requirements.txt..."
pip install -r "$REPO/requirements/dev.txt" --upgrade

deactivate
}

build_pyenv 2
build_pyenv 3
