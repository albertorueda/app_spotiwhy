#!/usr/bin/env bash

set -o errexit  # exit on error

pip3 install -r requirements.txt
pip install --upgrade django-cors-headers

python3 manage.py collectstatic --no-input