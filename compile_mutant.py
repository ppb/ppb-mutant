#!/usr/bin/env python
import os
import pathlib
import multiprocessing
from subprocess import run
import ppb_mutant

assetsdir = pathlib.Path(ppb_mutant.__file__).absolute().parent / '_assets'
rootdir = pathlib.Path(__file__).absolute().parent
mutantdir = rootdir / 'mutant'
orxdir = rootdir / 'orxporter'

run([
    str(orxdir / 'orxport.py'),
    '-m', str(mutantdir / 'manifest/out.orx'),
    '-i', str(mutantdir / 'input'),
    '-q', '32x32',
    '-o', str(assetsdir),
    '-F', 'png-64',
    '-t', str(multiprocessing.cpu_count() * 2),
    '-f', '%s',
], check=True)

run([
    str(orxdir / 'orxport.py'),
    '-m', str(mutantdir / 'manifest/out.orx'),
    '-j', str(rootdir / 'struct.json')
], check=True)
