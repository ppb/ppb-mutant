#!/bin/sh
set -e

rm -rf ppb_mutant/_assets/*
touch ppb_mutant/_assets/__init__.py

python3 ./download_zips.py
