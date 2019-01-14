#!/usr/bin/env python
import os
from subprocess import run

if os.path.exists('mutant'):
    run(['git', 'fetch'], cwd='mutant', check=True)
    run(['git', 'checkout', 'origin/master'], cwd='mutant', check=True)
else:
    run(['git', 'clone', 'https://github.com/mutantstandard/build.git', 'mutant'], check=True)


if os.path.exists('orxporter'):
    run(['git', 'fetch'], cwd='orxporter', check=True)
    run(['git', 'checkout', 'v0.1.0'], cwd='orxporter', check=True)
else:
    run(['git', 'clone', 'https://github.com/mutantstandard/orxporter.git'], check=True)
