#!/usr/bin/env python
import os
from subprocess import run

if os.path.exists('mutant'):
    run(['git', 'pull'], cwd='mutant', check=True)
else:
    run(['git', 'clone', 'https://github.com/mutantstandard/build.git', 'mutant'], check=True)


if os.path.exists('orxporter'):
    run(['git', 'pull'], cwd='orxporter', check=True)
else:
    run(['git', 'clone', 'https://github.com/mutantstandard/orxporter.git'], check=True)
