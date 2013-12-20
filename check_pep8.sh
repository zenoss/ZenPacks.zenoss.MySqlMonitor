#!/bin/bash

PY_FILES=$(find . -name '*.py')
python pep8.py --show-source $PY_FILES