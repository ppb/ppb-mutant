#!/bin/sh
set -e

rm -rf ppb_mutant/_assets/*
touch ppb_mutant/_assets/__init__.py

python3 ./download_mutant.py
python3 ./compile_mutant.py
python3 ./mutant_json.py
python3 ./download_zips.py

cd ppb_mutant/_assets
oxipng -sao 6 -i 0 *.png
