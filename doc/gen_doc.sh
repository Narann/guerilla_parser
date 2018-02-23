#!/usr/bin/env bash

export PYTHONPATH=../src:${PYTHONPATH}

sphinx-build -T -E -a -b html -D language=en . _build/html
